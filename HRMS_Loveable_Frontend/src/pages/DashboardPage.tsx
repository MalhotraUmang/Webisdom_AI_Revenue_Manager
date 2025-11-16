import { Header } from '@/components/Header';
import { CampaignForm } from '@/components/CampaignForm';
import { useAuth } from '@/hooks/useAuth';

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">Welcome back, {user?.name}!</h2>
          <p className="text-muted-foreground">Create and manage your marketing campaigns</p>
        </div>
        <CampaignForm />
      </div>
    </div>
  );
}
