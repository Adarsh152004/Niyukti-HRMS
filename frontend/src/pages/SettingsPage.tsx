import * as React from 'react';
import { Settings, Shield, Bell, Key, Database, Sliders, ToggleLeft } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { IS_DEMO_MODE } from '@/providers/data-provider';

export function SettingsPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        title="System &amp; Organization Settings"
        description="Configuration for AI autonomy bounds, authentication, notification webhooks, and provider API keys."
      />

      {IS_DEMO_MODE && (
        <div className="px-4 py-2.5 bg-warning-soft border border-warning/30 rounded-lg text-sm text-warning flex items-center justify-between">
          <span><strong>Demo Mode:</strong> Settings modifications are simulated locally for demonstration.</span>
          <Badge variant="warning" size="sm">Local Sandbox</Badge>
        </div>
      )}

      <Tabs defaultValue="ai-guardrails">
        <TabsList>
          <TabsTrigger value="ai-guardrails">AI Autonomy &amp; Guardrails</TabsTrigger>
          <TabsTrigger value="organization">Organization Profile</TabsTrigger>
          <TabsTrigger value="security">Security &amp; MFA</TabsTrigger>
          <TabsTrigger value="notifications">Notification Rules</TabsTrigger>
        </TabsList>

        <TabsContent value="ai-guardrails" className="space-y-4">
          <Card className="space-y-4">
            <CardHeader>
              <CardTitle>Autonomous Execution Bounds</CardTitle>
            </CardHeader>
            <div className="space-y-3 max-w-xl">
              <div className="flex items-center justify-between py-2 border-b border-border">
                <div>
                  <p className="text-sm font-medium text-text-primary">Enforce HITL on Compensation Alterations</p>
                  <p className="text-xs text-text-muted">Requires executive approval for any salary adjustment exceeding threshold</p>
                </div>
                <Badge variant="success" size="sm">Enforced</Badge>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-border">
                <div>
                  <p className="text-sm font-medium text-text-primary">Automated Resume Screening Threshold</p>
                  <p className="text-xs text-text-muted">Minimum confidence required before auto-advancing candidate to screening</p>
                </div>
                <span className="text-sm font-bold text-text-primary">85%</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-border">
                <div>
                  <p className="text-sm font-medium text-text-primary">Zero-Knowledge PII Masking</p>
                  <p className="text-xs text-text-muted">Sanitize Aadhaar / SSN / Bank Details before passing context to LLMs</p>
                </div>
                <Badge variant="success" size="sm">Active (Hardware Enclave)</Badge>
              </div>

              <div className="pt-2">
                <Button variant="primary" size="md">Save Policy Bounds</Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="organization">
          <Card className="space-y-4 max-w-xl">
            <CardHeader>
              <CardTitle>Legal Entity Details</CardTitle>
            </CardHeader>
            <div className="space-y-3">
              <Input label="Organization Legal Name" defaultValue="Apex Technologies Global Inc." />
              <Input label="Primary Operating Entity" defaultValue="India / Singapore / United States" />
              <Input label="Payroll Currency" defaultValue="USD ($) / INR (₹)" />
              <Button variant="primary" size="md">Update Details</Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="security">
          <Card className="space-y-4 max-w-xl">
            <CardHeader>
              <CardTitle>Enterprise Security Controls</CardTitle>
            </CardHeader>
            <div className="space-y-2 text-sm text-text-secondary">
              <p>• Mandatory FIDO2 / TOTP Two-Factor Authentication enforced on all Administrator &amp; Executive accounts.</p>
              <p>• Session timeout strictly set to 15 minutes of inactivity on elevated privilege roles.</p>
              <p>• All database queries signed through mutual TLS (mTLS) with role-based row-level security (RLS).</p>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card className="space-y-4 max-w-xl">
            <CardHeader>
              <CardTitle>Executive Notification Webhooks</CardTitle>
            </CardHeader>
            <div className="space-y-3">
              <Input label="Slack / Teams Webhook URL" placeholder="https://hooks.slack.com/services/..." defaultValue="https://hooks.slack.com/services/T00/B00/XXXXX" />
              <Input label="Escalation Email" defaultValue="executive-alerts@enterprise.demo" />
              <Button variant="primary" size="md">Test &amp; Save Webhook</Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
