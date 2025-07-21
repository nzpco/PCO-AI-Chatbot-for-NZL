"use client";

import { ChromaAutoRetriever } from "@/components/ChromaAutoRetriever";

export default function AutoRetrieverPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Chroma Auto Retriever</h1>
        <p className="text-muted-foreground">
          Search through legislation documents using natural language queries with automatic metadata filtering.
        </p>
      </div>
      <div className="w-full">
        <ChromaAutoRetriever />
      </div>
    </div>
  );
}