import React from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check, Clock, DollarSign, Users, ArrowRight, Zap } from 'lucide-react';
import LeadMagnetForm from '@/components/LeadMagnetForm';

const Index = () => {
  const [showForm, setShowForm] = React.useState(false);

  if (showForm) {
    return <LeadMagnetForm />;
  }

  return (
    <div className="min-h-screen gradient-bg">
      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-primary/10" />
        <div className="container mx-auto max-w-4xl text-center relative z-10">
          <div className="animate-fade-in">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight" style={{ color: 'hsl(200 50% 25%)' }}>
              Get Your Custom <span className="gradient-hero bg-clip-text text-transparent animate-pulse-soft">Automation Strategy</span> Report
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed animate-fade-in" style={{ animationDelay: '0.2s' }}>
              Discover exactly which automations will save your business 15+ hours per week
            </p>
          </div>

          {/* Social Proof Badges */}
          <div className="flex flex-wrap justify-center gap-4 mb-12 animate-slide-up" style={{ animationDelay: '0.4s' }}>
            <Badge variant="secondary" className="px-4 py-2 text-sm font-medium shadow-soft hover-lift transition-spring">
              <Check className="w-4 h-4 mr-2 text-success" />
              Used by 1,000+ businesses
            </Badge>
            <Badge variant="secondary" className="px-4 py-2 text-sm font-medium shadow-soft hover-lift transition-spring" style={{ animationDelay: '0.1s' }}>
              <DollarSign className="w-4 h-4 mr-2 text-success" />
              Average savings: $2,847/month
            </Badge>
            <Badge variant="secondary" className="px-4 py-2 text-sm font-medium shadow-soft hover-lift transition-spring" style={{ animationDelay: '0.2s' }}>
              <Clock className="w-4 h-4 mr-2 text-success" />
              Takes 3 minutes
            </Badge>
          </div>

          {/* CTA Button */}
          <div className="animate-scale-in" style={{ animationDelay: '0.6s' }}>
            <Button
              onClick={() => setShowForm(true)}
              className="bg-primary hover:bg-primary-hover text-primary-foreground text-lg px-12 py-4 rounded-full shadow-medium transition-spring hover:shadow-strong hover:scale-105 hover-glow animate-float"
            >
              <Zap className="w-5 h-5 mr-2" />
              Start My Free Assessment
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <p className="text-sm text-muted-foreground mt-4 animate-fade-in" style={{ animationDelay: '0.8s' }}>
              No signup required • Get instant results
            </p>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4 bg-primary/5">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16 animate-fade-in" style={{ color: 'hsl(200 50% 25%)' }}>
            What You'll Discover In Your Report
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="p-8 shadow-soft hover-lift gradient-card transition-spring animate-fade-in" style={{ animationDelay: '0.1s' }}>
              <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-6 mx-auto shadow-medium animate-float" style={{ animationDelay: '1s' }}>
                <Zap className="w-8 h-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-4 text-center" style={{ color: 'hsl(200 50% 25%)' }}>
                Quick Wins
              </h3>
              <p className="text-muted-foreground text-center leading-relaxed">
                3 automations you can implement this week to start saving time immediately, 
                tailored to your specific business needs.
              </p>
            </Card>

            <Card className="p-8 shadow-soft hover-lift gradient-card transition-spring animate-fade-in" style={{ animationDelay: '0.3s' }}>
              <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-6 mx-auto shadow-medium animate-float" style={{ animationDelay: '1.2s' }}>
                <Users className="w-8 h-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-4 text-center" style={{ color: 'hsl(200 50% 25%)' }}>
                Custom Roadmap
              </h3>
              <p className="text-muted-foreground text-center leading-relaxed">
                A 6-month implementation plan designed for your team size, 
                budget, and business goals.
              </p>
            </Card>

            <Card className="p-8 shadow-soft hover-lift gradient-card transition-spring animate-fade-in" style={{ animationDelay: '0.5s' }}>
              <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-6 mx-auto shadow-medium animate-float" style={{ animationDelay: '1.4s' }}>
                <DollarSign className="w-8 h-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-4 text-center" style={{ color: 'hsl(200 50% 25%)' }}>
                ROI Projections
              </h3>
              <p className="text-muted-foreground text-center leading-relaxed">
                Exact calculations of time and money savings, 
                plus tool recommendations that fit your budget.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-2xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6 animate-fade-in" style={{ color: 'hsl(200 50% 25%)' }}>
            Ready to Reclaim Your Time?
          </h2>
          <p className="text-xl text-muted-foreground mb-12 animate-fade-in" style={{ animationDelay: '0.2s' }}>
            Join 1,000+ business owners who've automated their way to more freedom
          </p>
          <div className="animate-scale-in" style={{ animationDelay: '0.4s' }}>
            <Button
              onClick={() => setShowForm(true)}
              className="bg-primary hover:bg-primary-hover text-primary-foreground text-lg px-12 py-4 rounded-full shadow-medium transition-spring hover:shadow-strong hover:scale-105 hover-glow"
            >
              Get My Custom Strategy Report
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
