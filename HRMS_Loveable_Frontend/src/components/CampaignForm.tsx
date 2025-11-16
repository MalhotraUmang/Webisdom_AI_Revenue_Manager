import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { toast } from 'sonner';
import { postCampaign } from '@/config/api';
import { format } from 'date-fns';
import { CalendarIcon, Send, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

export function CampaignForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    campaignText: '',
    targetClientCategory: '',
    startDate: undefined as Date | undefined,
    startTime: '09:00',
    endDate: undefined as Date | undefined,
    endTime: '17:00',
    campaignMessageCount: 1,
    messageTemplate1: '',
    messageTiming1: '09:00',
    messageTemplate2: '',
    messageTiming2: '12:00',
    messageTemplate3: '',
    messageTiming3: '15:00',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.campaignText || !formData.targetClientCategory || !formData.startDate || !formData.endDate) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (formData.campaignMessageCount < 1 || formData.campaignMessageCount > 10) {
      toast.error('Message count must be between 1 and 10');
      return;
    }

    // Validate message templates based on count
    if (formData.campaignMessageCount >= 1 && !formData.messageTemplate1) {
      toast.error('Please provide Message Template #1');
      return;
    }
    if (formData.campaignMessageCount >= 2 && !formData.messageTemplate2) {
      toast.error('Please provide Message Template #2');
      return;
    }
    if (formData.campaignMessageCount >= 3 && !formData.messageTemplate3) {
      toast.error('Please provide Message Template #3');
      return;
    }

    setIsSubmitting(true);

    try {
      // Format dates and times
      const startDateTime = `${format(formData.startDate, 'yyyy-MM-dd')} ${formData.startTime}`;
      const endDateTime = `${format(formData.endDate, 'yyyy-MM-dd')} ${formData.endTime}`;

      // Prepare payload
      const payload = {
        campaignText: formData.campaignText,
        targetClientCategory: formData.targetClientCategory,
        startDateTime,
        endDateTime,
        campaignMessageCount: formData.campaignMessageCount,
        messageTemplate1: formData.messageTemplate1,
        messageTiming1: formData.messageTiming1,
        messageTemplate2: formData.messageTemplate2 || '',
        messageTiming2: formData.messageTiming2,
        messageTemplate3: formData.messageTemplate3 || '',
        messageTiming3: formData.messageTiming3,
      };

      await postCampaign(payload);
      toast.success('Campaign created successfully!');
      
      // Reset form
      setFormData({
        campaignText: '',
        targetClientCategory: '',
        startDate: undefined,
        startTime: '09:00',
        endDate: undefined,
        endTime: '17:00',
        campaignMessageCount: 1,
        messageTemplate1: '',
        messageTiming1: '09:00',
        messageTemplate2: '',
        messageTiming2: '12:00',
        messageTemplate3: '',
        messageTiming3: '15:00',
      });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create campaign');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card className="shadow-medium">
        <CardHeader>
          <CardTitle>Campaign Details</CardTitle>
          <CardDescription>Configure your marketing campaign settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Campaign Text */}
          <div className="space-y-2">
            <Label htmlFor="campaignText">Campaign Text *</Label>
            <Textarea
              id="campaignText"
              placeholder="Enter your campaign description..."
              value={formData.campaignText}
              onChange={(e) => setFormData({ ...formData, campaignText: e.target.value })}
              rows={4}
              required
            />
          </div>

          {/* Target Category */}
          <div className="space-y-2">
            <Label htmlFor="targetCategory">Target Client Category *</Label>
            <Select
              value={formData.targetClientCategory}
              onValueChange={(value) => setFormData({ ...formData, targetClientCategory: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Solo">Solo</SelectItem>
                <SelectItem value="Family">Family</SelectItem>
                <SelectItem value="Business">Business</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Date/Time Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Start Date-Time */}
            <div className="space-y-4">
              <Label>Start Date & Time *</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      'w-full justify-start text-left font-normal',
                      !formData.startDate && 'text-muted-foreground'
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {formData.startDate ? format(formData.startDate, 'PPP') : 'Pick a date'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={formData.startDate}
                    onSelect={(date) => setFormData({ ...formData, startDate: date })}
                    initialFocus
                    className="pointer-events-auto"
                  />
                </PopoverContent>
              </Popover>
              <div className="relative">
                <Clock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  type="time"
                  value={formData.startTime}
                  onChange={(e) => setFormData({ ...formData, startTime: e.target.value })}
                  className="pl-10"
                  required
                />
              </div>
            </div>

            {/* End Date-Time */}
            <div className="space-y-4">
              <Label>End Date & Time *</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      'w-full justify-start text-left font-normal',
                      !formData.endDate && 'text-muted-foreground'
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {formData.endDate ? format(formData.endDate, 'PPP') : 'Pick a date'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={formData.endDate}
                    onSelect={(date) => setFormData({ ...formData, endDate: date })}
                    initialFocus
                    className="pointer-events-auto"
                  />
                </PopoverContent>
              </Popover>
              <div className="relative">
                <Clock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  type="time"
                  value={formData.endTime}
                  onChange={(e) => setFormData({ ...formData, endTime: e.target.value })}
                  className="pl-10"
                  required
                />
              </div>
            </div>
          </div>

          {/* Message Count */}
          <div className="space-y-2">
            <Label htmlFor="messageCount">Campaign Message Count (1-10) *</Label>
            <Input
              id="messageCount"
              type="number"
              min="1"
              max="10"
              value={formData.campaignMessageCount}
              onChange={(e) => setFormData({ ...formData, campaignMessageCount: parseInt(e.target.value) || 1 })}
              required
            />
          </div>
        </CardContent>
      </Card>

      {/* Message Templates */}
      <Card className="shadow-medium">
        <CardHeader>
          <CardTitle>Message Templates</CardTitle>
          <CardDescription>Configure your campaign messages and timing</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Message 1 */}
          {formData.campaignMessageCount >= 1 && (
            <div className="space-y-4 p-4 rounded-lg border bg-muted/30">
              <h4 className="font-semibold text-sm">Message #1</h4>
              <div className="space-y-2">
                <Label htmlFor="template1">Message Template *</Label>
                <Textarea
                  id="template1"
                  placeholder="Enter message template..."
                  value={formData.messageTemplate1}
                  onChange={(e) => setFormData({ ...formData, messageTemplate1: e.target.value })}
                  rows={3}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="timing1">Send Time *</Label>
                <div className="relative">
                  <Clock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="timing1"
                    type="time"
                    value={formData.messageTiming1}
                    onChange={(e) => setFormData({ ...formData, messageTiming1: e.target.value })}
                    className="pl-10"
                    required
                  />
                </div>
              </div>
            </div>
          )}

          {/* Message 2 */}
          {formData.campaignMessageCount >= 2 && (
            <div className="space-y-4 p-4 rounded-lg border bg-muted/30">
              <h4 className="font-semibold text-sm">Message #2</h4>
              <div className="space-y-2">
                <Label htmlFor="template2">Message Template *</Label>
                <Textarea
                  id="template2"
                  placeholder="Enter message template..."
                  value={formData.messageTemplate2}
                  onChange={(e) => setFormData({ ...formData, messageTemplate2: e.target.value })}
                  rows={3}
                  required={formData.campaignMessageCount >= 2}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="timing2">Send Time *</Label>
                <div className="relative">
                  <Clock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="timing2"
                    type="time"
                    value={formData.messageTiming2}
                    onChange={(e) => setFormData({ ...formData, messageTiming2: e.target.value })}
                    className="pl-10"
                    required={formData.campaignMessageCount >= 2}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Message 3 */}
          {formData.campaignMessageCount >= 3 && (
            <div className="space-y-4 p-4 rounded-lg border bg-muted/30">
              <h4 className="font-semibold text-sm">Message #3</h4>
              <div className="space-y-2">
                <Label htmlFor="template3">Message Template *</Label>
                <Textarea
                  id="template3"
                  placeholder="Enter message template..."
                  value={formData.messageTemplate3}
                  onChange={(e) => setFormData({ ...formData, messageTemplate3: e.target.value })}
                  rows={3}
                  required={formData.campaignMessageCount >= 3}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="timing3">Send Time *</Label>
                <div className="relative">
                  <Clock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="timing3"
                    type="time"
                    value={formData.messageTiming3}
                    onChange={(e) => setFormData({ ...formData, messageTiming3: e.target.value })}
                    className="pl-10"
                    required={formData.campaignMessageCount >= 3}
                  />
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Submit Button */}
      <div className="flex justify-end">
        <Button type="submit" size="lg" disabled={isSubmitting} className="min-w-[200px]">
          {isSubmitting ? (
            <>Submitting...</>
          ) : (
            <>
              <Send className="mr-2 h-4 w-4" />
              Create Campaign
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
