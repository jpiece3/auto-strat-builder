import React from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Check, Mail, FileText, Target, Zap, TrendingUp } from 'lucide-react';

const ThankYou: React.FC = () => {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto text-center">
          {/* Success Header */}
          <div className="mb-12 animate-fade-in">
            <div className="w-20 h-20 bg-success rounded-full flex items-center justify-center mx-auto mb-6 animate-scale-in">
              <Check className="w-10 h-10 text-success-foreground" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              🎉 Your Custom Automation Strategy Report is on its way!
            </h1>
            <p className="text-xl text-muted-foreground mb-8">
              Check your email in the next 5 minutes
            </p>
          </div>

          {/* What's Included */}
          <Card className="p-8 shadow-medium gradient-card animate-slide-up mb-8">
            <h2 className="text-2xl font-bold text-foreground mb-8">
              Here's what's included in your personalized report:
            </h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div className="flex items-start gap-4 p-6 rounded-lg bg-accent/30 hover:bg-accent/50 transition-smooth">
                <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                  <Zap className="w-6 h-6 text-primary-foreground" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-foreground mb-2">3 Immediate Quick Wins</h3>
                  <p className="text-muted-foreground text-sm">
                    Simple automations you can implement this week to start saving time immediately
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-6 rounded-lg bg-accent/30 hover:bg-accent/50 transition-smooth">
                <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="w-6 h-6 text-primary-foreground" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-foreground mb-2">High-Impact Opportunities</h3>
                  <p className="text-muted-foreground text-sm">
                    Ranked by ROI potential based on your specific business needs and current setup
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-6 rounded-lg bg-accent/30 hover:bg-accent/50 transition-smooth">
                <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                  <Target className="w-6 h-6 text-primary-foreground" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-foreground mb-2">6-Month Roadmap</h3>
                  <p className="text-muted-foreground text-sm">
                    Step-by-step implementation timeline tailored to your team size and goals
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-6 rounded-lg bg-accent/30 hover:bg-accent/50 transition-smooth">
                <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileText className="w-6 h-6 text-primary-foreground" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-foreground mb-2">Exact Tools & Setup</h3>
                  <p className="text-muted-foreground text-sm">
                    Detailed instructions and tool recommendations based on your current tech stack
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-8 p-6 rounded-lg bg-success/10 border border-success/20">
              <div className="flex items-center justify-center gap-3 mb-3">
                <TrendingUp className="w-6 h-6 text-success" />
                <h3 className="text-lg font-semibold text-success">Projected Savings</h3>
              </div>
              <p className="text-success font-medium">
                Based on your responses, we estimate this strategy will save you 15+ hours per week 
                and $2,847+ per month in operational efficiency
              </p>
            </div>
          </Card>

          {/* Next Steps */}
          <Card className="p-8 shadow-soft animate-slide-up">
            <div className="flex items-center justify-center gap-3 mb-6">
              <Mail className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">What happens next?</h2>
            </div>
            
            <div className="space-y-4 text-left max-w-2xl mx-auto">
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-primary font-semibold text-sm">1</span>
                </div>
                <p className="text-muted-foreground">
                  <strong className="text-foreground">Check your email</strong> - Your personalized report will arrive within 5 minutes
                </p>
              </div>
              
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-primary font-semibold text-sm">2</span>
                </div>
                <p className="text-muted-foreground">
                  <strong className="text-foreground">Review your quick wins</strong> - Start with the 3 immediate actions we've identified
                </p>
              </div>
              
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-primary font-semibold text-sm">3</span>
                </div>
                <p className="text-muted-foreground">
                  <strong className="text-foreground">Optional: Book a strategy call</strong> - We'll include a link to discuss implementation with our team
                </p>
              </div>
            </div>
          </Card>

          {/* CTA */}
          <div className="mt-12 text-center animate-fade-in">
            <Button 
              onClick={() => window.location.href = '/'}
              className="gradient-hero hover:opacity-90 text-lg px-8 py-3"
            >
              Create Another Report
            </Button>
            <p className="text-sm text-muted-foreground mt-4">
              Want to help a colleague? Share this assessment with your team!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThankYou;