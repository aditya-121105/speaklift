import { Metadata } from "next";
import { PageContainer } from "@/components/layout/page-container";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/layout/empty-state";
import { Activity } from "lucide-react";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "SpeakLift Dashboard.",
};

export default function DashboardPage() {
  return (
    <PageContainer>
      <PageHeader 
        title="Dashboard" 
        description="Welcome to your AI Career Coach. Here's an overview of your progress."
      />
      <EmptyState 
        title="No activity yet"
        description="Your dashboard will populate once you complete your first interview session."
        icon={Activity}
      />
    </PageContainer>
  );
}
