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
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-50 opacity-50" />
        <div className="container mx-auto max-w-4xl text-center relative z-10">
          <div className="animate-fade-in">
            <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-6 leading-tight">
              Get Your Custom <span className="bg-gradient-to-r from-primary via-blue-600 to-blue-700 bg-clip-text text-transparent">Automation Strategy</span> Report
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
              Discover exactly which automations will save your business 15+ hours per week
            </p>
          </div>

          {/* Social Proof Badges */}
          <div className="flex flex-wrap justify-center gap-4 mb-12 animate-slide-up">
            <Badge variant="secondary" className="px-4 py-2 text-sm font-medium shadow-soft">
              <Check className="w-4 h-4 mr-2 text-success" />
              Used by 1,000+ businesses
            </Badge>
            <Badge variant="secondary" className="px-4 py-2 text-sm font-medium shadow-soft">
              <DollarSign className="w-4 h-4 mr-2 text-success" />
              Average savings: $2,847/month
            </Badge>
            <Badge variant="secondary" className="px-4 py-2 text-sm font-medium shadow-soft">
              <Clock className="w-4 h-4 mr-2 text-success" />
              Takes 3 minutes
            </Badge>
          </div>

          {/* CTA Button */}
          <div className="animate-scale-in">
            <Button
              onClick={() => setShowForm(true)}
              className="bg-gradient-to-r from-primary via-blue-600 to-blue-700 text-primary-foreground hover:opacity-90 text-lg px-12 py-4 rounded-full shadow-medium transition-all hover:shadow-strong hover:scale-105"
            >
              <Zap className="w-5 h-5 mr-2" />
              Start My Free Assessment
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <p className="text-sm text-muted-foreground mt-4">
              No signup required • Get instant results
            </p>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4 bg-accent/20">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-foreground mb-16">
            What You'll Discover In Your Report
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8 animate-fade-in">
            <Card className="p-8 shadow-soft hover:shadow-medium transition-all hover:-translate-y-2 gradient-card">
              <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-6 mx-auto">
                <Zap className="w-8 h-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-4 text-center">
                Quick Wins
              </h3>
              <p className="text-muted-foreground text-center leading-relaxed">
                3 automations you can implement this week to start saving time immediately, 
                tailored to your specific business needs.
              </p>
            </Card>

            <Card className="p-8 shadow-soft hover:shadow-medium transition-all hover:-translate-y-2 gradient-card">
              <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-6 mx-auto">
                <Users className="w-8 h-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-4 text-center">
                Custom Roadmap
              </h3>
              <p className="text-muted-foreground text-center leading-relaxed">
                A 6-month implementation plan designed for your team size, 
                budget, and business goals.
              </p>
            </Card>

            <Card className="p-8 shadow-soft hover:shadow-medium transition-all hover:-translate-y-2 gradient-card">
              <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mb-6 mx-auto">
                <DollarSign className="w-8 h-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-4 text-center">
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
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-6">
            Ready to Reclaim Your Time?
          </h2>
          <p className="text-xl text-muted-foreground mb-12">
            Join 1,000+ business owners who've automated their way to more freedom
          </p>
          <Button
            onClick={() => setShowForm(true)}
            className="bg-gradient-to-r from-primary via-blue-600 to-blue-700 text-primary-foreground hover:opacity-90 text-lg px-12 py-4 rounded-full shadow-medium transition-all hover:shadow-strong hover:scale-105"
          >
            Get My Custom Strategy Report
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </section>
    </div>
  );
};

export default Index;
