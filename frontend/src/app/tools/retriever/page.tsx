"use client";

import { NaiveVectorRetriever } from "@/components/NaiveVectorRetriever";

export default function RetrieverPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Semantic Search Retriever</h1>
        <p className="text-muted-foreground mb-2">
          Enter a natural language query to find the most relevant fragments of legislation. This tool uses AI-powered semantic search to match your query to the meaning of legislative text, not just keywords.
        </p>
        <ul className="list-disc pl-6 text-muted-foreground mb-2">
          <li>Results show the most relevant fragments, along with a &quot;score&quot; indicating the strength of the match.</li>
          <li>This is an experimental tool and may not return comprehensive results.</li>
        </ul>
        <p className="text-muted-foreground text-sm">
          <strong>Tip:</strong> Try searching for a concept or requirement, not just a section number.
        </p>
      </div>
      <div className="w-full">
        <NaiveVectorRetriever />
      </div>
    </div>
  );
}