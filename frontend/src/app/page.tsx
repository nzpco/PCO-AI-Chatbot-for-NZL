import { Inter } from "next/font/google";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
  return (
    <div className={`flex min-h-screen flex-col items-center p-8 bg-[#fef7ee] ${inter.className}`}>
      <div className="mb-8">
        <Image
          src="/owl.png"
          alt="Wise Owl"
          width={200}
          height={200}
          priority
        />
      </div>
      <Card className="w-full max-w-3xl">
        <CardHeader>
          <CardTitle className="text-3xl font-extrabold mb-2 text-center">Chat with New Zealand Legislation</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4 text-lg text-muted-foreground text-center">
            Ask factual questions about New Zealand law and get relevant legislative sections, powered by AI. This is the main way to explore and test the prototype.
          </p>
          <p className="text-lg text-muted-foreground mb-4 text-center">
            You can also:
          </p>
          <ul className="list-disc pl-6 text-muted-foreground mb-4">
            <li>Browse the structured legislative data model and AI-generated context summaries.</li>
            <li>Experiment with retrieval tools that find relevant legislative fragments using semantic search.</li>
          </ul>
          <p className="text-muted-foreground text-sm text-center">
            <strong>Note:</strong> This is a research prototype. Answers are experimental and not legal advice.
          </p>
        </CardContent>
        <CardFooter className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button asChild size="lg">
            <Link href="/chat">Start Chatting</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/legislation">Browse Legislation</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/tools/retriever">Try the Retriever</Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
