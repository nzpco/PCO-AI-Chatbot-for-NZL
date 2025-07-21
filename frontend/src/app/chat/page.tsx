import Chat from "@/components/Chat";

export default function ChatPage() {
  return (
    <div className="container p-8">
      <div className="mb-4 bg-muted rounded-md p-4 text-muted-foreground text-center text-sm">
        Ask factual questions about New Zealand legislation.<br />
        <strong>Note:</strong> This is a research prototype—answers are experimental and not legal advice.
      </div>
      <Chat inputPlaceholder="Ask a factual question about legislation" />
    </div>
  );
}