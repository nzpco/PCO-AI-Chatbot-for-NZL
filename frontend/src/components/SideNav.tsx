"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  BookOpen,
  Search,
  FileText,
  Wrench,
  FileSearch,
  Bot
} from "lucide-react";

const navigation = [
  {
    title: "Chat",
    href: "/chat",
    icon: Bot,
  },
  {
    title: "Legislation",
    href: "/legislation",
    icon: FileText,
  },
  {
    title: "Tools",
    href: "/tools",
    icon: Wrench,
    children: [
      {
        title: "Query fragments",
        href: "/tools/query-engine",
        icon: Search,
      },
      {
        title: "Query documents",
        href: "/tools/document-query",
        icon: FileSearch,
      },
    ],
  },
];

export function SideNav() {
  const pathname = usePathname();

  return (
    <div className="w-64 border-r bg-background">
      <div className="flex h-14 items-center border-b px-4">
        <Link href="/" className="flex items-center gap-2">
          <BookOpen className="h-6 w-6" />
          <span className="font-semibold">PCO Chatbot</span>
        </Link>
      </div>
      <ScrollArea className="h-[calc(100vh-3.5rem)]">
        <div className="space-y-1 p-2">
          {navigation.map((item) => (
            <div key={item.href}>
              <Button
                variant={pathname === item.href ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start gap-2",
                  pathname === item.href && "bg-accent"
                )}
                asChild
                title={
                  item.title === "Legislation"
                    ? "Explore the internal data model and context summaries used for retrieval."
                    : item.title === "Chat"
                    ? "Try the chat assistant, which uses retrieval tools to answer factual questions about legislation."
                    : item.title === "Tools"
                    ? "Experiment with the core retrieval tools available to the chatbot."
                    : undefined
                }
              >
                <Link href={item.href}>
                  <item.icon className="h-4 w-4" />
                  {item.title}
                </Link>
              </Button>
              {item.children && (
                <div className="ml-4 mt-1 space-y-1">
                  {item.children.map((child) => (
                    <Button
                      key={child.href}
                      variant={pathname === child.href ? "secondary" : "ghost"}
                      className={cn(
                        "w-full justify-start gap-2",
                        pathname === child.href && "bg-accent"
                      )}
                      asChild
                    >
                      <Link href={child.href}>
                        <child.icon className="h-4 w-4" />
                        {child.title}
                      </Link>
                    </Button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}