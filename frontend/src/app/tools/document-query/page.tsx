'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { FragmentViewer } from '@/components/legislation/fragment-viewer';
import { toast } from 'sonner';
import { RetrievedFragment } from '@/types/legislation';
import ReactMarkdown from 'react-markdown';

interface QueryResponse {
  answer: string;
  results: RetrievedFragment[];
  metadata: {
    filters: Record<string, string>;
    query: string;
    top_k: number;
  };
}

export default function DocumentQueryPage() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const res = await fetch('/api/tools/query-documents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          top_k: 5,
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to query legislation');
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error('Query error:', err);
      toast.error('Failed to query legislation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Document Query Engine</h1>
        <p className="text-muted-foreground">
          Find relevant legislation documents (Acts) based on your questions. This tool searches at the document level rather than specific sections.
        </p>
      </div>
      <div className="w-full space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Ask a question to find relevant legislation documents..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={isLoading}
            />
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Querying...' : 'Query'}
            </Button>
          </div>
        </form>

        {response && (
          <div className="space-y-6">
            <div className="rounded-lg border p-4 bg-muted">
              <h3 className="font-semibold mb-2">Answer:</h3>
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown>{response.answer}</ReactMarkdown>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Retrieved Documents:</h3>
              <div className="space-y-4">
                {response.results.map((result, index) => (
                  <FragmentViewer
                    key={index}
                    fragment={result.fragment}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}