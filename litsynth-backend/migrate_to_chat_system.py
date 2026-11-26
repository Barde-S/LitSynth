#!/usr/bin/env python3
"""
Migration Script: Add Chat table and migrate existing ChatMessages

This migration:
1. Creates default "General Chat" for workspaces that have messages but no chats
2. Migrates orphaned messages (workspace_id set, chat_id null) to the default chat
3. Updates message counts for all chats

Run this script ONCE after deploying the new Chat model.
"""

import sys
import os
from uuid import uuid4
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlmodel import Session, select, create_engine
from models import Workspace, Chat, ChatMessage

def migrate_to_chat_system():
    """Migrate existing workspace messages to chat-based system"""

    # Connect to database
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'db', 'litsynth.db')
    engine = create_engine(f"sqlite:///{db_path}")

    print("=" * 70)
    print("LitSynth: Migrating to Chat-based System")
    print("=" * 70)
    print()

    with Session(engine) as session:
        # Step 1: Get all workspaces
        workspaces = session.exec(select(Workspace)).all()
        print(f"Found {len(workspaces)} workspace(s)")
        print()

        total_migrated = 0
        workspaces_updated = 0

        for workspace in workspaces:
            print(f"Processing workspace: '{workspace.name}' ({workspace.workspace_id})")

            # Step 2: Check if workspace already has chats
            existing_chats = session.exec(
                select(Chat).where(Chat.workspace_id == workspace.workspace_id)
            ).all()

            if existing_chats:
                print(f"  ✓ Already has {len(existing_chats)} chat(s)")

                # Update message counts for existing chats
                for chat in existing_chats:
                    msg_count = len(session.exec(
                        select(ChatMessage).where(ChatMessage.chat_id == chat.chat_id)
                    ).all())

                    if chat.message_count != msg_count:
                        chat.message_count = msg_count
                        session.add(chat)
                        print(f"  ✓ Updated '{chat.title}' message count: {msg_count}")

                session.commit()
                print()
                continue

            # Step 3: Find orphaned messages (workspace_id set, chat_id null)
            orphaned_messages = session.exec(
                select(ChatMessage)
                .where(ChatMessage.workspace_id == workspace.workspace_id)
                .where(ChatMessage.chat_id == None)
                .order_by(ChatMessage.created_at)
            ).all()

            if not orphaned_messages:
                print(f"  ℹ️  No orphaned messages found")
                print()
                continue

            print(f"  Found {len(orphaned_messages)} orphaned message(s)")

            # Step 4: Create default "General Chat"
            default_chat = Chat(
                chat_id=str(uuid4()),
                workspace_id=workspace.workspace_id,
                title="General Chat",
                message_count=len(orphaned_messages),
                created_at=orphaned_messages[0].created_at,
                updated_at=orphaned_messages[-1].created_at
            )
            session.add(default_chat)
            session.commit()
            session.refresh(default_chat)

            print(f"  ✓ Created 'General Chat' ({default_chat.chat_id})")

            # Step 5: Migrate orphaned messages to default chat
            for message in orphaned_messages:
                message.chat_id = default_chat.chat_id
                session.add(message)

            session.commit()

            print(f"  ✓ Migrated {len(orphaned_messages)} message(s) to 'General Chat'")
            print()

            total_migrated += len(orphaned_messages)
            workspaces_updated += 1

        print("=" * 70)
        print("Migration Summary")
        print("=" * 70)
        print(f"Workspaces processed: {len(workspaces)}")
        print(f"Workspaces updated: {workspaces_updated}")
        print(f"Total messages migrated: {total_migrated}")
        print()
        print("✅ Migration complete!")
        print("=" * 70)

if __name__ == "__main__":
    try:
        migrate_to_chat_system()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
