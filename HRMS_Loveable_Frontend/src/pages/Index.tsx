import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/Header';
import { Calendar, Users, Target, TrendingUp, LogIn, UserPlus } from 'lucide-react';

export default function Index() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen bg-gradient-hero">
      <Header />
      
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto">
          <div className="inline-flex items-center justify-center p-3 bg-gradient-primary rounded-2xl mb-6 shadow-medium">
            <Calendar className="h-12 w-12 text-primary-foreground" />
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-6">
            HRMS Campaign Manager
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Streamline your marketing campaigns with our powerful automation platform. 
            Target clients effectively and schedule campaigns with precision.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="shadow-medium">
              <Link to="/register">
                <UserPlus className="mr-2 h-5 w-5" />
                Get Started
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="shadow-soft">
              <Link to="/login">
                <LogIn className="mr-2 h-5 w-5" />
                Sign In
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div className="bg-card rounded-xl p-6 shadow-soft hover:shadow-medium transition-all">
            <div className="bg-gradient-primary rounded-lg p-3 w-fit mb-4">
              <Target className="h-6 w-6 text-primary-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">Targeted Campaigns</h3>
            <p className="text-muted-foreground">
              Segment clients by Solo, Family, or Business categories for precise targeting.
            </p>
          </div>

          <div className="bg-card rounded-xl p-6 shadow-soft hover:shadow-medium transition-all">
            <div className="bg-gradient-accent rounded-lg p-3 w-fit mb-4">
              <Calendar className="h-6 w-6 text-accent-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">Smart Scheduling</h3>
            <p className="text-muted-foreground">
              Schedule campaigns with exact date and time control for optimal engagement.
            </p>
          </div>

          <div className="bg-card rounded-xl p-6 shadow-soft hover:shadow-medium transition-all">
            <div className="bg-gradient-primary rounded-lg p-3 w-fit mb-4">
              <Users className="h-6 w-6 text-primary-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">Multi-Message</h3>
            <p className="text-muted-foreground">
              Create up to 10 messages per campaign with custom templates and timings.
            </p>
          </div>

          <div className="bg-card rounded-xl p-6 shadow-soft hover:shadow-medium transition-all">
            <div className="bg-gradient-accent rounded-lg p-3 w-fit mb-4">
              <TrendingUp className="h-6 w-6 text-accent-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">Real-time Sync</h3>
            <p className="text-muted-foreground">
              Seamlessly integrates with Google Sheets for instant data updates.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="bg-card rounded-2xl p-12 shadow-large max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-foreground mb-4">
            Ready to transform your marketing?
          </h2>
          <p className="text-muted-foreground mb-8">
            Join marketing teams who trust our platform for their campaign management.
          </p>
          <Button asChild size="lg" className="shadow-medium">
            <Link to="/register">
              Start Your Free Campaign
            </Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
