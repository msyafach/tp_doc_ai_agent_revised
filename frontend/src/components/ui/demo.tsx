import {
  Sidebar,
  SidebarProvider,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  SidebarHeader,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import {
  Calendar,
  ChevronsUpDown,
  Home,
  Inbox,
  Leaf,
  Search,
  Settings,
  User,
} from "lucide-react";

const items = [
  { title: "Home", url: "#", icon: Home },
  { title: "Inbox", url: "#", icon: Inbox },
  { title: "Calendar", url: "#", icon: Calendar },
  { title: "Search", url: "#", icon: Search },
  { title: "Settings", url: "#", icon: Settings },
];

export function SidebarDemo() {
  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
          <div className="flex items-center gap-2 rounded-md px-2 py-1">
            <Leaf className="h-5 w-5 text-brand-green" />
            <span className="text-sm font-semibold">TP Generator</span>
          </div>
        </SidebarHeader>

        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Application</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {items.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild tooltip={item.title}>
                      <a href={item.url}>
                        <item.icon />
                        <span>{item.title}</span>
                      </a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter>
          <SidebarGroup>
            <SidebarMenuButton className="h-12 w-full justify-between gap-3">
              <div className="flex items-center gap-2">
                <User className="h-5 w-5 rounded-md" />
                <div className="flex flex-col items-start">
                  <span className="text-sm font-medium">John Doe</span>
                  <span className="text-xs text-muted-foreground">
                    john@example.com
                  </span>
                </div>
              </div>
              <ChevronsUpDown className="h-5 w-5 rounded-md" />
            </SidebarMenuButton>
          </SidebarGroup>
        </SidebarFooter>
      </Sidebar>

      <main className="min-h-screen flex-1">
        <div className="px-4 py-2">
          <SidebarTrigger className="mt-2 h-4 w-4" />
        </div>
        <div className="p-6">
          <h1 className="text-2xl font-bold">Main Content</h1>
          <p className="mt-2">This is the main content area of the page.</p>
        </div>
      </main>
    </SidebarProvider>
  );
}
