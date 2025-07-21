"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { FragmentViewer } from "@/components/legislation/fragment-viewer"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"

interface LegislationDocument {
  _id: string
  title: string
  year: string
  type: string
  no: string
}

export default function LegislationDocumentPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const router = useRouter()
  const { id } = React.use(params)
  const [document, setDocument] = React.useState<LegislationDocument | null>(null)
  const [rootFragments, setRootFragments] = React.useState<any[]>([])

  // Fetch document and root fragments on mount
  React.useEffect(() => {
    fetch(`/api/legislation/${id}`)
      .then((res) => res.json())
      .then((data) => {
        setDocument(data.document)
        setRootFragments(data.root_fragments)
      })
      .catch(console.error)
  }, [id])

  if (!document) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center gap-4 mb-8">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/legislation")}
          className="gap-2"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Documents
        </Button>
        <h1 className="text-2xl font-bold">{document.title}</h1>
      </div>

      <div className="space-y-8">
        {rootFragments.map((fragment) => (
          <FragmentViewer
            key={fragment._id}
            fragment={fragment}
            initialExpanded={true}
          />
        ))}
      </div>
    </div>
  )
}