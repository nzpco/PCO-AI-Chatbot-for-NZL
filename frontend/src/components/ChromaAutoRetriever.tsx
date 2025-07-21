"use client";

import React, { useState } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { FragmentViewer } from "@/components/legislation/fragment-viewer";

interface RetrievedFragment {
  fragment: Parameters<typeof FragmentViewer>[0]["fragment"];
  score: number;
}

interface RetrievalMetadata {
  filters: Record<string, string | number | boolean>;
  query: string;
  top_k: number;
  vector_query?: string;
}

interface RetrievalResponse {
  results: RetrievedFragment[];
  metadata: RetrievalMetadata;
}

export function ChromaAutoRetriever() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<RetrievalResponse | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/tools/auto-retrieve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Failed to retrieve results');
      }

      const data = await response.json();
      console.log('API Response:', data); // Debug log
      setResponse(data);
    } catch (error) {
      console.error('Error retrieving results:', error);
      setResponse(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          placeholder="Enter your query (e.g. 'Show me recent legislation about climate change')..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <Button onClick={handleSearch} disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Searching...
            </>
          ) : (
            'Search'
          )}
        </Button>
      </div>

      {response && (
        <div className="text-sm text-muted-foreground bg-muted/30 p-3 rounded-md">
          <pre className="whitespace-pre-wrap">
            {JSON.stringify(response.metadata, null, 2)}
          </pre>
        </div>
      )}

      <div className="space-y-4">
        {response?.results.length ? (
          response.results.map((result, index) => (
            <div key={index} className="space-y-2">
              <div className="text-sm text-muted-foreground">
                Score: {result.score.toFixed(4)}
              </div>
              <FragmentViewer fragment={result.fragment} />
            </div>
          ))
        ) : (
          <div className="text-muted-foreground text-center py-8">
            {isLoading ? "Searching..." : "No results yet. Try searching for something."}
          </div>
        )}
      </div>
    </div>
  );
}