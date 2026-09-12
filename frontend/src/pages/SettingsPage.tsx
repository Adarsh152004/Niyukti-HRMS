import * as React from 'react';
import { Settings, Shield, Bell, Key, Database, Sliders, CheckCircle2, X } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

export function SettingsPage() {
  const [toastMessage, setToastMessage] = React.useState<string | null>(null);
  const [orgName, setOrgName] = React.useState('Azyntrix AI Technologies Inc.');
  const [orgEntity, setOrgEntity] = React.useState('India / Singapore / United States');
  const [payrollCurrency, setPayrollCurrency] = React.useState('USD ($) / INR (₹)');

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  return (
    <div className="space-y-5 pb-10">
      <PageHeader
        title="System &amp; Organization Settings"
        description="Configuration for AI autonomy bounds, authentication, notification webhooks, and provider API keys."
      />

      {toastMessage && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center justify-between shadow-xs">
          <span className="flex items-center gap-2 font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            {toastMessage}
          </span>
          <button onClick={() => setToastMessage(null)} className="text-emerald-600 hover:text-emerald-900">
            <X className="w-3.5 h-3.5" />
          </button>
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
                <span className="text-sm font-bold font-mono text-emerald-600">85% Match</span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-border">
                <div>
                  <p className="text-sm font-medium text-text-primary">Zero-Knowledge PII Masking</p>
                  <p className="text-xs text-text-muted">Sanitize Aadhaar / SSN / Bank Details before passing context to LLMs</p>
                </div>
                <Badge variant="success" size="sm">Active (Hardware KMS)</Badge>
              </div>

              <div className="pt-2">
                <Button variant="primary" size="md" onClick={() => showToast('AI Autonomy & Guardrails policies updated and enforced.')}>
                  Save Policy Bounds
                </Button>
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
              <Input 
                label="Organization Legal Name" 
                value={orgName} 
                onChange={(e) => setOrgName(e.target.value)} 
              />
              <Input 
                label="Primary Operating Entity" 
                value={orgEntity} 
                onChange={(e) => setOrgEntity(e.target.value)} 
              />
              <Input 
                label="Payroll Currency" 
                value={payrollCurrency} 
                onChange={(e) => setPayrollCurrency(e.target.value)} 
              />
              <Button variant="primary" size="md" onClick={() => showToast('Organization profile details updated successfully.')}>
                Update Details
              </Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="security">
          <Card className="space-y-4 max-w-xl">
            <CardHeader>
              <CardTitle>Enterprise Security Controls</CardTitle>
            </CardHeader>
            <div className="space-y-2.5 text-xs text-text-secondary">
              <div className="flex items-start gap-2 bg-surface-secondary p-3 rounded-lg border border-border">
                <Shield className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-text-primary">Mandatory FIDO2 / Passkey / TOTP Authentication</p>
                  <p className="text-text-muted">Enforced on all Executive and Administrator privileged operations.</p>
                </div>
              </div>
              <div className="flex items-start gap-2 bg-surface-secondary p-3 rounded-lg border border-border">
                <Key className="w-4 h-4 text-accent shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-text-primary">mTLS &amp; Row-Level Security (RLS)</p>
                  <p className="text-text-muted">All database transactions encrypted with cryptographic identity verification.</p>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card className="space-y-4 max-w-xl">
            <CardHeader>
              <CardTitle>Executive Notification Webhooks</CardTitle>
            </CardHeader>
            <div className="space-y-3">
              <Input label="WhatsApp Webhook Endpoint" defaultValue="https://api.azyntrix.com/v1/notifications/whatsapp" />
              <Input label="Slack Escalation Channel" defaultValue="#executive-alerts-live" />
              <Button variant="secondary" size="md" onClick={() => showToast('Test ping dispatched to configured webhook channels.')}>
                Send Test Webhook Ping
              </Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
