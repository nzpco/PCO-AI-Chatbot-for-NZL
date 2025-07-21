import * as React from "react"
import { ChevronRight, ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"

interface TreeItemProps {
  label: string
  id: string
  children?: React.ReactNode
  onSelect?: (id: string) => void
  isSelected?: boolean
  className?: string
}

const TreeItem = React.forwardRef<HTMLDivElement, TreeItemProps>(
  ({ label, id, children, onSelect, isSelected, className }, ref) => {
    const [isExpanded, setIsExpanded] = React.useState(false)
    const hasChildren = React.Children.count(children) > 0

    return (
      <div ref={ref} className={cn("", className)}>
        <div
          className={cn(
            "flex items-center gap-1 px-2 py-1 rounded-md cursor-pointer hover:bg-accent",
            isSelected && "bg-accent"
          )}
          onClick={() => {
            if (hasChildren) {
              setIsExpanded(!isExpanded)
            }
            onSelect?.(id)
          }}
        >
          {hasChildren && (
            <span className="w-4 h-4 flex items-center justify-center">
              {isExpanded ? (
                <ChevronDown className="w-3 h-3" />
              ) : (
                <ChevronRight className="w-3 h-3" />
              )}
            </span>
          )}
          <span className="text-sm">{label}</span>
        </div>
        {isExpanded && hasChildren && (
          <div className="ml-4 border-l pl-2">{children}</div>
        )}
      </div>
    )
  }
)
TreeItem.displayName = "TreeItem"

interface TreeProps {
  items: {
    id: string
    label: string
    children?: TreeProps["items"]
  }[]
  onSelect?: (id: string) => void
  selectedId?: string
  className?: string
}

const Tree = React.forwardRef<HTMLDivElement, TreeProps>(
  ({ items, onSelect, selectedId, className }, ref) => {
    return (
      <div ref={ref} className={cn("", className)}>
        {items.map((item) => (
          <TreeItem
            key={item.id}
            id={item.id}
            label={item.label}
            onSelect={onSelect}
            isSelected={selectedId === item.id}
          >
            {item.children && (
              <Tree
                items={item.children}
                onSelect={onSelect}
                selectedId={selectedId}
              />
            )}
          </TreeItem>
        ))}
      </div>
    )
  }
)
Tree.displayName = "Tree"

export { Tree, TreeItem }