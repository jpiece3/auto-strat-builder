import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ChevronRight, ChevronLeft, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from '@/hooks/use-toast';

interface FormData {
  timeEater: string;
  teamSize: string;
  businessType: string;
  magicWand: string;
  timeSpent: string;
  revenue: string;
  tools: string[];
  goal: string;
  name: string;
  email: string;
  company: string;
}

interface Question {
  id: keyof FormData;
  question: string;
  type: 'radio' | 'checkbox' | 'contact';
  options?: string[];
}

const questions: Question[] = [
  {
    id: 'timeEater',
    question: "What's eating up most of your time right now?",
    type: 'radio',
    options: [
      'Manual scheduling/booking',
      'Following up with leads',
      'Data entry/admin work',
      'Customer support requests',
      'Creating content/marketing',
      'Managing team communication'
    ]
  },
  {
    id: 'teamSize',
    question: "How big is your team?",
    type: 'radio',
    options: ['Just me', '2-5 people', '6-15 people', '16+ people']
  },
  {
    id: 'businessType',
    question: "What type of business do you run?",
    type: 'radio',
    options: [
      'Service-based (coaching, consulting, agency)',
      'E-commerce/retail',
      'SaaS/tech',
      'Local business (restaurant, salon, etc.)',
      'Other'
    ]
  },
  {
    id: 'magicWand',
    question: "If you could wave a magic wand and automate ONE thing tomorrow, what would free up the most mental energy?",
    type: 'radio',
    options: [
      'Never having to manually schedule again',
      'Leads automatically getting nurtured',
      'All my data entry happening behind the scenes',
      'Customer questions answering themselves',
      'My team staying in sync without me',
      'My marketing running itself'
    ]
  },
  {
    id: 'timeSpent',
    question: "How much time per week do you currently spend on repetitive tasks?",
    type: 'radio',
    options: ['Less than 5 hours', '5-10 hours', '10-20 hours', 'More than 20 hours']
  },
  {
    id: 'revenue',
    question: "What's your current monthly revenue range?",
    type: 'radio',
    options: ['Under $10k', '$10k-$50k', '$50k-$100k', '$100k+', 'Prefer not to say']
  },
  {
    id: 'tools',
    question: "Which tools do you currently use? (Select all that apply)",
    type: 'checkbox',
    options: [
      'None/Basic email',
      'CRM (Salesforce, HubSpot)',
      'Email marketing (Mailchimp, ConvertKit)',
      'Project management (Asana, Monday)',
      'Scheduling (Calendly, Acuity)',
      'E-commerce platform (Shopify, WooCommerce)'
    ]
  }
];

const LeadMagnetForm: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    timeEater: '',
    teamSize: '',
    businessType: '',
    magicWand: '',
    timeSpent: '',
    revenue: '',
    tools: [],
    goal: '',
    name: '',
    email: '',
    company: ''
  });

  const navigate = useNavigate();
  const totalSteps = 8;
  const progressPercentage = ((currentStep + 1) / totalSteps) * 100;

  const handleInputChange = (field: keyof FormData, value: string | string[]) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Webhook submission (placeholder URL)
      const response = await fetch('https://webhook.placeholder.url/automation-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      // Navigate to thank you page regardless of response for demo
      navigate('/thank-you');
    } catch (error) {
      // For demo purposes, still navigate to thank you page
      navigate('/thank-you');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isCurrentStepValid = () => {
    if (currentStep === 7) {
      return formData.goal && formData.name && formData.email;
    }
    
    const currentQuestion = questions[currentStep];
    if (!currentQuestion) return false;
    
    if (currentQuestion.type === 'checkbox') {
      return formData[currentQuestion.id as keyof FormData].length > 0;
    }
    
    return formData[currentQuestion.id as keyof FormData] !== '';
  };

  const renderQuestion = () => {
    if (currentStep === 7) {
      // Final step: Question 8 + Contact Form
      return (
        <div className="space-y-8 animate-fade-in">
          <div>
            <h3 className="text-xl font-semibold text-foreground mb-6">
              What's your biggest business goal for the next 6 months?
            </h3>
            <RadioGroup
              value={formData.goal}
              onValueChange={(value) => handleInputChange('goal', value)}
              className="space-y-3"
            >
              {[
                'Scale my team without chaos',
                'Increase revenue by 25%+',
                'Free up 10+ hours/week for strategy',
                'Improve customer experience',
                'Streamline operations',
                'Launch new products/services'
              ].map((option) => (
                <div key={option} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-accent/50 transition-smooth">
                  <RadioGroupItem value={option} id={option} />
                  <Label htmlFor={option} className="flex-1 cursor-pointer text-sm font-medium">
                    {option}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>

          <div className="border-t pt-8">
            <h3 className="text-lg font-semibold text-foreground mb-6">
              Almost done! Just need your contact info to send your report:
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name" className="text-sm font-medium">
                  Name <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="mt-1"
                  placeholder="Your full name"
                />
              </div>
              <div>
                <Label htmlFor="email" className="text-sm font-medium">
                  Email <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="mt-1"
                  placeholder="your@email.com"
                />
              </div>
              <div className="md:col-span-2">
                <Label htmlFor="company" className="text-sm font-medium">
                  Company (optional)
                </Label>
                <Input
                  id="company"
                  type="text"
                  value={formData.company}
                  onChange={(e) => handleInputChange('company', e.target.value)}
                  className="mt-1"
                  placeholder="Your company name"
                />
              </div>
            </div>
          </div>
        </div>
      );
    }

    const question = questions[currentStep];
    
    return (
      <div className="space-y-6 animate-fade-in">
        <h3 className="text-xl font-semibold text-foreground mb-8">
          {question.question}
        </h3>
        
        {question.type === 'radio' && (
          <RadioGroup
            value={formData[question.id as keyof FormData] as string}
            onValueChange={(value) => handleInputChange(question.id, value)}
            className="space-y-3"
          >
            {question.options?.map((option) => (
              <div key={option} className="flex items-center space-x-3 p-4 rounded-lg hover:bg-accent/50 transition-smooth">
                <RadioGroupItem value={option} id={option} />
                <Label htmlFor={option} className="flex-1 cursor-pointer font-medium">
                  {option}
                </Label>
              </div>
            ))}
          </RadioGroup>
        )}
        
        {question.type === 'checkbox' && (
          <div className="space-y-3">
            {question.options?.map((option) => (
              <div key={option} className="flex items-center space-x-3 p-4 rounded-lg hover:bg-accent/50 transition-smooth">
                <Checkbox
                  id={option}
                  checked={formData.tools.includes(option)}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      handleInputChange('tools', [...formData.tools, option]);
                    } else {
                      handleInputChange('tools', formData.tools.filter(tool => tool !== option));
                    }
                  }}
                />
                <Label htmlFor={option} className="flex-1 cursor-pointer font-medium">
                  {option}
                </Label>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Progress Bar */}
      <div className="w-full bg-secondary/30 h-2">
        <div 
          className="h-full gradient-hero transition-all duration-700 ease-out"
          style={{ width: `${progressPercentage}%` }}
        />
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          {/* Progress Indicator */}
          <div className="text-center mb-8">
            <div className="text-sm text-muted-foreground mb-2">
              Question {currentStep + 1} of {totalSteps}
            </div>
            <div className="text-primary font-semibold">
              {Math.round(progressPercentage)}% Complete
            </div>
          </div>

          {/* Question Card */}
          <Card className="p-8 shadow-medium gradient-card animate-scale-in">
            {renderQuestion()}
          </Card>

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className="flex items-center gap-2"
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </Button>

            {currentStep === totalSteps - 1 ? (
              <Button
                onClick={handleSubmit}
                disabled={!isCurrentStepValid() || isSubmitting}
                className="flex items-center gap-2 gradient-hero hover:opacity-90"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Check className="w-4 h-4" />
                    Get My Report
                  </>
                )}
              </Button>
            ) : (
              <Button
                onClick={handleNext}
                disabled={!isCurrentStepValid()}
                className="flex items-center gap-2"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeadMagnetForm;