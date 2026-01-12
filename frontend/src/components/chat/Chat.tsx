import { ChatHeader } from "@/components/chat/ChatHeader";
import { Composer } from "@/components/chat/Composer";
import { MessageList } from "@/components/chat/MessageList";
import type { ChatModel, Citation, Document, Message } from "@/types/api";

interface ChatProps {
  document: Document | null;
  messages: Message[];
  models: ChatModel[];
  selectedModel: string;
  messageLoading: boolean;
  messageError: unknown;
  busy: boolean;
  deleting: boolean;
  reindexing: boolean;
  draftPrompt: string | null;
  onModelChange: (model: string) => void;
  onDeleteDocument: () => void;
  onReindex: () => void;
  onRetryMessages: () => void;
  onSend: (message: string) => void;
  onPrompt: (prompt: string) => void;
  onShowSources: (citations: Citation[]) => void;
  onFeedback: (messageId: string, rating: -1 | 1) => void;
}

export function Chat(props: ChatProps) {
  return (
    <section className="flex h-full min-h-0 min-w-0 flex-col overflow-hidden bg-white">
      <ChatHeader document={props.document} models={props.models} selectedModel={props.selectedModel} deleting={props.deleting} reindexing={props.reindexing} onModelChange={props.onModelChange} onDelete={props.onDeleteDocument} onReindex={props.onReindex} />
      <MessageList document={props.document} messages={props.messages} loading={props.messageLoading} error={props.messageError} onRetry={props.onRetryMessages} onPrompt={props.onPrompt} onShowSources={props.onShowSources} onFeedback={props.onFeedback} onReindex={props.onReindex} />
      <Composer documentStatus={props.document?.status ?? null} busy={props.busy} draftPrompt={props.draftPrompt} onSend={props.onSend} />
    </section>
  );
}
