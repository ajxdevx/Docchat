import { ConversationList } from "@/components/conversations/ConversationList";
import { DocumentList } from "@/components/documents/DocumentList";
import type { Conversation, Document, DocumentStatus } from "@/types/api";

interface LibrarySidebarProps {
  documents: Document[];
  conversations: Conversation[];
  selectedDocumentId: string | null;
  selectedConversationId: string | null;
  selectedDocumentStatus: DocumentStatus | null;
  search: string;
  documentsLoading: boolean;
  documentsError: unknown;
  conversationsLoading: boolean;
  conversationsError: unknown;
  creatingConversation: boolean;
  deletingConversationId: string | null;
  uploadProgress: number | null;
  uploading: boolean;
  allowedExtensions: string[];
  maxFileMb: number;
  onSearch: (value: string) => void;
  onSelectDocument: (id: string) => void;
  onSelectConversation: (id: string) => void;
  onCreateConversation: () => void;
  onDeleteConversation: (id: string) => void;
  onUpload: (file: File) => void;
  onRetryDocuments: () => void;
  onRetryConversations: () => void;
}

export function LibrarySidebar(props: LibrarySidebarProps) {
  return (
    <div className="h-full min-h-0 overflow-hidden bg-[#f8f9fa]">
      <div className="h-full overflow-y-auto overscroll-contain">
        <DocumentList
          documents={props.documents}
          selectedId={props.selectedDocumentId}
          search={props.search}
          loading={props.documentsLoading}
          error={props.documentsError}
          allowedExtensions={props.allowedExtensions}
          maxFileMb={props.maxFileMb}
          uploadProgress={props.uploadProgress}
          uploading={props.uploading}
          onSearch={props.onSearch}
          onSelect={props.onSelectDocument}
          onUpload={props.onUpload}
          onRetry={props.onRetryDocuments}
        />
        {props.selectedDocumentStatus && (
          <ConversationList
            conversations={props.conversations}
            selectedId={props.selectedConversationId}
            documentStatus={props.selectedDocumentStatus}
            loading={props.conversationsLoading}
            error={props.conversationsError}
            creating={props.creatingConversation}
            deletingId={props.deletingConversationId}
            onSelect={props.onSelectConversation}
            onCreate={props.onCreateConversation}
            onDelete={props.onDeleteConversation}
            onRetry={props.onRetryConversations}
          />
        )}
      </div>
    </div>
  );
}
