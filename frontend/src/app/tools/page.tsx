"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Search, FileText } from "lucide-react";

export default function ToolsPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Tools</h1>
        <p className="text-muted-foreground">
          Explore our collection of tools for analyzing and understanding legislation.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Query Fragments
            </CardTitle>
            <CardDescription>
              Search for specific fragments of legislation using natural language queries.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/tools/query-engine">Open Tool</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Query Documents
            </CardTitle>
            <CardDescription>
              Search across entire legislative documents (Acts) using natural language queries.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/tools/document-query">Open Tool</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}