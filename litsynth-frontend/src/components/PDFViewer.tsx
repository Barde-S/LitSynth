import { useState, useCallback, useEffect, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import { ZoomIn, ZoomOut, Search, X } from 'lucide-react';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PDFViewerProps {
  url: string;
  initialPage?: number;
  highlightText?: string;
  className?: string;
}

/**
 * Normalize text for fuzzy matching: collapse whitespace, strip common
 * PDF artifacts (hyphenation, ligatures), lowercase, trim.
 */
function normalizeText(text: string): string {
  return text
    .replace(/\ufb01/g, 'fi')   // fi ligature
    .replace(/\ufb02/g, 'fl')   // fl ligature
    .replace(/\ufb00/g, 'ff')   // ff ligature
    .replace(/\ufb03/g, 'ffi')  // ffi ligature
    .replace(/\ufb04/g, 'ffl')  // ffl ligature
    .replace(/-\s*\n\s*/g, '')  // hyphenation at line breaks
    .replace(/\s+/g, ' ')
    .toLowerCase()
    .trim();
}

/**
 * Walk the text layer spans on the target page, concatenate their text,
 * find where highlightText appears, then apply a highlight background
 * to the matching spans. Returns true if highlighting succeeded.
 */
function highlightSpansInTextLayer(
  pageElement: HTMLDivElement,
  highlightText: string
): boolean {
  const textLayer = pageElement.querySelector('.react-pdf__Page__textContent');
  if (!textLayer) return false;

  const spans = Array.from(textLayer.querySelectorAll('span')) as HTMLSpanElement[];
  if (spans.length === 0) return false;

  // Build a map: for each span, record its start index in the concatenated page text
  const spanOffsets: { span: HTMLSpanElement; start: number; end: number; text: string }[] = [];
  let fullText = '';

  for (const span of spans) {
    const raw = span.textContent || '';
    const start = fullText.length;
    fullText += raw;
    spanOffsets.push({ span, start, end: fullText.length, text: raw });
  }

  // Normalize both the full page text and the highlight text for matching
  const normalizedHighlight = normalizeText(highlightText);
  if (normalizedHighlight.length < 3) return false;

  // Build normalized version of fullText with index mapping back to original
  const normMap: number[] = [];
  let normalized = '';
  let prevWasSpace = false;

  const fullTextNorm = fullText
    .replace(/\ufb01/g, 'fi')
    .replace(/\ufb02/g, 'fl')
    .replace(/\ufb00/g, 'ff')
    .replace(/\ufb03/g, 'ffi')
    .replace(/\ufb04/g, 'ffl');

  for (let i = 0; i < fullTextNorm.length; i++) {
    const ch = fullTextNorm[i];
    if (/\s/.test(ch)) {
      if (!prevWasSpace && normalized.length > 0) {
        normalized += ' ';
        normMap.push(i);
        prevWasSpace = true;
      }
    } else {
      normalized += ch.toLowerCase();
      normMap.push(i);
      prevWasSpace = false;
    }
  }

  // Try to find the highlight text in the normalized page text
  let matchStart = -1;
  let matchLen = 0;

  // Strategy 1: Full match
  matchStart = normalized.indexOf(normalizedHighlight);
  if (matchStart !== -1) {
    matchLen = normalizedHighlight.length;
  }

  // Strategy 2: Remove words from the end progressively
  if (matchStart === -1) {
    const words = normalizedHighlight.split(' ');
    for (let w = words.length - 1; w >= 3; w--) {
      const searchStr = words.slice(0, w).join(' ');
      matchStart = normalized.indexOf(searchStr);
      if (matchStart !== -1) {
        matchLen = searchStr.length;
        break;
      }
    }
  }

  // Strategy 3: Try a short fragment from the middle of the highlight text
  if (matchStart === -1) {
    const words = normalizedHighlight.split(' ');
    if (words.length > 6) {
      // Try from word 2 onwards (skip potentially noisy start)
      for (let start = 1; start < Math.min(4, words.length - 3); start++) {
        const fragment = words.slice(start, start + 5).join(' ');
        matchStart = normalized.indexOf(fragment);
        if (matchStart !== -1) {
          matchLen = fragment.length;
          break;
        }
      }
    }
  }

  if (matchStart === -1 || matchLen === 0) return false;

  // Map normalized indices back to original fullText indices
  const origStart = normMap[matchStart];
  const origEnd = normMap[Math.min(matchStart + matchLen - 1, normMap.length - 1)] + 1;

  // Find which spans overlap [origStart, origEnd) and highlight them
  let highlighted = false;
  for (const entry of spanOffsets) {
    if (entry.end <= origStart || entry.start >= origEnd) continue;
    entry.span.style.backgroundColor = 'rgba(250, 204, 21, 0.4)';
    entry.span.style.borderRadius = '2px';
    entry.span.classList.add('citation-highlight');
    highlighted = true;
  }

  return highlighted;
}

export default function PDFViewer({
  url,
  initialPage = 1,
  highlightText,
  className = ''
}: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [scale, setScale] = useState<number>(1.2);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [renderedPages, setRenderedPages] = useState<Set<number>>(new Set());

  // Search state
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showSearch, setShowSearch] = useState<boolean>(false);
  const [activeSearchText, setActiveSearchText] = useState<string>('');

  // Refs for scrolling
  const containerRef = useRef<HTMLDivElement>(null);
  const pageRefs = useRef<Map<number, HTMLDivElement>>(new Map());
  const searchInputRef = useRef<HTMLInputElement>(null);
  const hasScrolledRef = useRef<boolean>(false);
  const hasHighlightedRef = useRef<boolean>(false);

  // Scroll to page function
  const scrollToPage = useCallback((pageNum: number) => {
    const pageElement = pageRefs.current.get(pageNum);
    if (pageElement && containerRef.current) {
      pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return true;
    }
    return false;
  }, []);

  // Scroll to initial page as soon as TARGET page is rendered (not all pages)
  useEffect(() => {
    if (hasScrolledRef.current) return;
    if (numPages > 0 && initialPage >= 1 && initialPage <= numPages && renderedPages.has(initialPage)) {
      const timer = setTimeout(() => {
        if (!hasScrolledRef.current) {
          scrollToPage(initialPage);
          hasScrolledRef.current = true;
        }
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [initialPage, numPages, renderedPages, scrollToPage]);

  // Apply citation highlighting once target page is rendered, with retries
  useEffect(() => {
    if (hasHighlightedRef.current) return;
    if (!highlightText || initialPage < 1) return;
    if (!renderedPages.has(initialPage)) return;

    const pageEl = pageRefs.current.get(initialPage);
    if (!pageEl) return;

    // Retry highlighting with increasing delays — text layer may populate after render
    const delays = [200, 600, 1200, 2000];
    let attempt = 0;
    let cancelled = false;

    const tryHighlight = () => {
      if (cancelled || hasHighlightedRef.current) return;

      const success = highlightSpansInTextLayer(pageEl, highlightText);
      if (success) {
        hasHighlightedRef.current = true;
        const firstHighlight = pageEl.querySelector('.citation-highlight');
        if (firstHighlight) {
          firstHighlight.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return;
      }

      // Schedule next retry
      attempt++;
      if (attempt < delays.length) {
        setTimeout(tryHighlight, delays[attempt]);
      }
    };

    const timer = setTimeout(tryHighlight, delays[0]);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [renderedPages, highlightText, initialPage]);

  // Reset scroll/highlight state when props change (new citation clicked)
  useEffect(() => {
    hasScrolledRef.current = false;
    hasHighlightedRef.current = false;
  }, [initialPage, highlightText]);

  // Focus search input when search is opened
  useEffect(() => {
    if (showSearch && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [showSearch]);

  // Keyboard shortcut for search (Ctrl/Cmd + F)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        setShowSearch(true);
      }
      if (e.key === 'Escape' && showSearch) {
        setShowSearch(false);
        setSearchQuery('');
        setActiveSearchText('');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showSearch]);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setRenderedPages(new Set());
    hasScrolledRef.current = false;
    hasHighlightedRef.current = false;
    setLoading(false);
    setError(null);
  };

  const onDocumentLoadError = (err: Error) => {
    setError('Failed to load PDF');
    setLoading(false);
    console.error('PDF load error:', err);
  };

  const onPageRenderSuccess = useCallback((pageNum: number) => {
    setRenderedPages(prev => {
      const next = new Set(prev);
      next.add(pageNum);
      return next;
    });
  }, []);

  const zoomIn = () => {
    setScale((prev) => Math.min(prev + 0.2, 3));
  };

  const zoomOut = () => {
    setScale((prev) => Math.max(prev - 0.2, 0.5));
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setActiveSearchText(searchQuery.trim());
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setActiveSearchText('');
  };

  const toggleSearch = () => {
    if (showSearch) {
      setShowSearch(false);
      setSearchQuery('');
      setActiveSearchText('');
    } else {
      setShowSearch(true);
    }
  };

  // Text renderer for search highlighting only (citation highlighting is done via DOM)
  const searchTextRenderer = useCallback(
    (textItem: { str: string }) => {
      const text = textItem.str;

      if (activeSearchText && activeSearchText.length >= 2) {
        const searchLower = activeSearchText.toLowerCase();
        const textLower = text.toLowerCase();
        const searchIndex = textLower.indexOf(searchLower);

        if (searchIndex !== -1) {
          const before = text.substring(0, searchIndex);
          const match = text.substring(searchIndex, searchIndex + activeSearchText.length);
          const after = text.substring(searchIndex + activeSearchText.length);
          return `${before}<mark class="bg-orange-400 dark:bg-orange-500 px-0.5 rounded">${match}</mark>${after}`;
        }
      }

      return text;
    },
    [activeSearchText]
  );

  // Store page ref
  const setPageRef = (pageNum: number) => (el: HTMLDivElement | null) => {
    if (el) {
      pageRefs.current.set(pageNum, el);
    }
  };

  // Handle page number input
  const handlePageInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 1 && value <= numPages) {
      scrollToPage(value);
    }
  };

  // Handle direct page jump button
  const handleGoToPage = () => {
    if (initialPage >= 1 && initialPage <= numPages) {
      scrollToPage(initialPage);
    }
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Controls */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex-wrap gap-2">
        {/* Page Navigation */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600 dark:text-gray-300">Go to:</span>
          <input
            type="number"
            min={1}
            max={numPages}
            placeholder="Page"
            className="w-16 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            onChange={handlePageInputChange}
          />
          <span className="text-sm text-gray-600 dark:text-gray-300">
            of {numPages || '?'}
          </span>
          {initialPage > 1 && (
            <button
              onClick={handleGoToPage}
              className="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              title={`Jump to citation page ${initialPage}`}
            >
              → p.{initialPage}
            </button>
          )}
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={zoomOut}
            disabled={scale <= 0.5}
            className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
            title="Zoom out"
          >
            <ZoomOut size={18} />
          </button>
          <span className="text-sm text-gray-600 dark:text-gray-300 min-w-[50px] text-center">
            {Math.round(scale * 100)}%
          </span>
          <button
            onClick={zoomIn}
            disabled={scale >= 3}
            className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
            title="Zoom in"
          >
            <ZoomIn size={18} />
          </button>
        </div>

        {/* Search Toggle & Highlight Indicator */}
        <div className="flex items-center gap-3">
          <button
            onClick={toggleSearch}
            className={`p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 ${showSearch ? 'bg-gray-200 dark:bg-gray-700' : ''}`}
            title="Search (Ctrl+F)"
          >
            <Search size={18} />
          </button>

          {highlightText && (
            <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
              <span className="w-3 h-3 bg-yellow-300 dark:bg-yellow-500 rounded-sm"></span>
              <span>Citation</span>
            </div>
          )}
        </div>
      </div>

      {/* Search Bar */}
      {showSearch && (
        <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-750 border-b border-gray-200 dark:border-gray-700">
          <form onSubmit={handleSearch} className="flex items-center gap-2 flex-1">
            <div className="relative flex-1 max-w-md">
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search in document..."
                className="w-full px-3 py-1.5 pr-8 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X size={16} />
                </button>
              )}
            </div>
            <button
              type="submit"
              className="px-3 py-1.5 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              Search
            </button>
          </form>

          {activeSearchText && (
            <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
              <span className="w-3 h-3 bg-orange-400 dark:bg-orange-500 rounded-sm"></span>
              <span>Search: "{activeSearchText}"</span>
            </div>
          )}
        </div>
      )}

      {/* PDF Content - Continuous Scroll */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto bg-gray-200 dark:bg-gray-900"
      >
        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600"></div>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center h-full text-red-500">
            {error}
          </div>
        )}

        <Document
          file={url}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={onDocumentLoadError}
          loading={null}
          className="flex flex-col items-center py-4 gap-4"
        >
          {/* Render all pages for continuous scroll */}
          {Array.from(new Array(numPages), (_, index) => {
            const pageNum = index + 1;
            return (
              <div
                key={`page_${pageNum}`}
                ref={setPageRef(pageNum)}
                className="relative"
              >
                {/* Page number indicator */}
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-gray-700 dark:bg-gray-600 text-white text-xs rounded-full opacity-70">
                  Page {pageNum}
                </div>
                <Page
                  pageNumber={pageNum}
                  scale={scale}
                  customTextRenderer={activeSearchText ? searchTextRenderer : undefined}
                  className="shadow-lg"
                  renderAnnotationLayer={true}
                  renderTextLayer={true}
                  onRenderSuccess={() => onPageRenderSuccess(pageNum)}
                />
              </div>
            );
          })}
        </Document>
      </div>
    </div>
  );
}
