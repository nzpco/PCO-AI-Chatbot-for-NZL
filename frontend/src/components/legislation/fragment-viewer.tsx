import * as React from "react"
import { Button } from "@/components/ui/button"
import { ChevronDown, ChevronRight } from "lucide-react"
import { LegislationFragment } from "@/types/legislation"
import { cn } from "@/lib/utils"
import { Label } from "@/components/ui/label"

interface FragmentViewerProps {
  fragment: LegislationFragment
  level?: number
  initialExpanded?: boolean
}

export function FragmentViewer({ fragment, level = 0, initialExpanded = false }: FragmentViewerProps) {
  const [isExpanded, setIsExpanded] = React.useState(initialExpanded)
  const [children, setChildren] = React.useState<FragmentViewerProps["fragment"][]>([])
  const [isLoading, setIsLoading] = React.useState(false)
  const [expandedFields, setExpandedFields] = React.useState<Record<string, boolean>>({})

  // Fetch children on mount if initially expanded
  React.useEffect(() => {
    if (initialExpanded && children.length === 0) {
      setIsLoading(true)
      fetch(`/api/legislation/fragment/${fragment._id}`)
        .then((res) => res.json())
        .then((data) => {
          const serializedChildren = data.child_fragments.map((child: FragmentViewerProps["fragment"]) => ({
            ...child,
            _id: child._id || child.chunk_id
          }))
          setChildren(serializedChildren)
        })
        .catch((error) => {
          console.error("Error fetching fragment:", error)
        })
        .finally(() => {
          setIsLoading(false)
        })
    }
  }, [fragment._id, initialExpanded, children.length])

  const getHeading = () => {
    if (!fragment.heading) return null
    return fragment.descriptive_label
      ? `${fragment.descriptive_label}: ${fragment.heading}`
      : fragment.heading
  }

  const handleExpand = async () => {
    if (!isExpanded && children.length === 0) {
      setIsLoading(true)
      try {
        const res = await fetch(`/api/legislation/fragment/${fragment._id}`)
        const data = await res.json()
        const serializedChildren = data.child_fragments.map((child: FragmentViewerProps["fragment"]) => ({
          ...child,
          _id: child._id || child.chunk_id
        }))
        setChildren(serializedChildren)
      } catch (error) {
        console.error("Error fetching fragment:", error)
      } finally {
        setIsLoading(false)
      }
    }
    setIsExpanded(!isExpanded)
  }

  const toggleField = (field: string) => {
    setExpandedFields(prev => ({
      ...prev,
      [field]: !prev[field]
    }))
  }

  const renderField = (label: string, value: string | null | undefined, isLongContent = false) => {
    if (!value) return null

    if (isLongContent) {
      const isExpanded = expandedFields[label]
      const previewText = value.length > 200 ? value.slice(0, 200) + "..." : value

      return (
        <div className="flex items-start gap-2">
          <Label className="text-muted-foreground min-w-[120px]">{label}</Label>
          <div className="flex-1">
            <div
              className={cn(
                "text-sm rounded-md p-2",
                label === "Text"
                  ? "font-mono whitespace-pre-wrap cursor-pointer hover:bg-accent/50 transition-colors"
                  : label === "Detailed Summary"
                    ? "whitespace-pre-wrap cursor-pointer hover:bg-accent/50 transition-colors"
                    : "bg-muted/50 italic"
              )}
              onClick={() => label === "Text" || label === "Detailed Summary" ? toggleField(label) : undefined}
            >
              {label === "Context" ? value : (isExpanded ? value : previewText)}
            </div>
          </div>
        </div>
      )
    }

    return (
      <div className="flex items-start gap-2">
        <Label className="text-muted-foreground min-w-[120px]">{label}</Label>
        <div className="text-sm bg-muted/50 rounded-md p-2 italic flex-1">
          {value}
        </div>
      </div>
    )
  }

  return (
    <div
      className="leg-fragment border-l-3 border-gray-300 pl-4 space-y-2"
      style={{ marginLeft: level === 0 ? "0" : "3rem" }}
    >
      {/* Fragment header */}
      <div className="flex items-start gap-2">
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0"
          onClick={handleExpand}
        >
          {isExpanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </Button>
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
            <div className="text-sm font-mono text-muted-foreground">
              {fragment.chunk_id}
            </div>
            <div className="text-sm text-muted-foreground">
              [{fragment.token_count} tokens]
            </div>
          </div>
          {getHeading() && (
            <h2 className="text-xl font-semibold">{getHeading()}</h2>
          )}
          {!isExpanded && fragment.summary && (
            <div className="text-sm bg-muted/50 rounded-md p-2 italic">
              {fragment.summary}
            </div>
          )}
        </div>
      </div>

      {/* Fragment fields - only shown when expanded */}
      {isExpanded && (
        <div className="space-y-2 pl-10">
          {renderField("Summary", fragment.summary)}
          {renderField("Detailed Summary", fragment.summary_long, true)}
          {renderField("Context", fragment.summary_context, true)}
          {renderField("Text", fragment.text, true)}
        </div>
      )}

      {/* Children */}
      {isExpanded && children.length > 0 && (
        <div className="space-y-4">
          {children.map((child) => (
            <FragmentViewer
              key={child._id}
              fragment={child}
              level={1}
            />
          ))}
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="text-sm text-muted-foreground pl-10">
          Loading...
        </div>
      )}
    </div>
  )
}