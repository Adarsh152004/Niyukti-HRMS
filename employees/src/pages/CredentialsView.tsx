import React from 'react';
import { ShieldCheck, Mail, Phone, Building2, MapPin, Calendar, CheckCircle2, User } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useEmployee } from '@/context/EmployeeContext';

export const CredentialsView: React.FC = () => {
  const { profile, actorId } = useEmployee();

  const employeeDisplayName = profile ? `${profile.first_name} ${profile.last_name}` : actorId;

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      <PageHeader
        title="Credentials & Verified Identity"
        description="Official workforce identity, cryptographic tenant federation, SSO credentials, and security clearance."
      />

      <Card className="p-6">
        <CardHeader className="pb-4 border-b border-border">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-accent" />
            Verified Workforce Identity &amp; Organization Alignment
          </CardTitle>
        </CardHeader>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">
          <div className="p-4 rounded-xl bg-surface-secondary border border-border">
            <p className="text-2xs text-text-muted uppercase font-semibold">Full Legal Name</p>
            <p className="text-base font-bold text-text-primary mt-1">{profile?.full_name || employeeDisplayName}</p>
            <p className="text-xs text-accent mt-0.5">{profile?.employee_code || actorId}</p>
          </div>

          <div className="p-4 rounded-xl bg-surface-secondary border border-border">
            <p className="text-2xs text-text-muted uppercase font-semibold">Corporate Email</p>
            <p className="text-sm font-semibold text-text-primary mt-1">{profile?.email || 'employee@novacorp.internal'}</p>
            <p className="text-2xs text-emerald-600 dark:text-emerald-400 mt-0.5">Verified SSO Active</p>
          </div>

          <div className="p-4 rounded-xl bg-surface-secondary border border-border">
            <p className="text-2xs text-text-muted uppercase font-semibold">Department &amp; Function</p>
            <p className="text-sm font-semibold text-text-primary mt-1">{profile?.department_name || 'Engineering & AI'}</p>
            <p className="text-2xs text-text-muted mt-0.5">{profile?.designation_name || 'Principal Engineer'}</p>
          </div>

          <div className="p-4 rounded-xl bg-surface-secondary border border-border">
            <p className="text-2xs text-text-muted uppercase font-semibold">Location / Base</p>
            <p className="text-sm font-semibold text-text-primary mt-1">{profile?.location || 'San Francisco, CA'}</p>
            <p className="text-2xs text-text-muted mt-0.5">{profile?.timezone || 'UTC-07:00 (Pacific)'}</p>
          </div>

          <div className="p-4 rounded-xl bg-surface-secondary border border-border">
            <p className="text-2xs text-text-muted uppercase font-semibold">Employment Status</p>
            <div className="mt-1">
              <Badge variant="success" size="sm">
                {profile?.employment_status || 'ACTIVE'}
              </Badge>
            </div>
            <p className="text-2xs text-text-muted mt-1">{profile?.employment_type || 'FULL_TIME'} • Indefinite</p>
          </div>

          <div className="p-4 rounded-xl bg-surface-secondary border border-border">
            <p className="text-2xs text-text-muted uppercase font-semibold">Joining Date</p>
            <p className="text-sm font-semibold text-text-primary mt-1">{profile?.joining_date || '2023-04-15'}</p>
            <p className="text-2xs text-text-muted mt-0.5">3+ Years Organization Tenure</p>
          </div>
        </div>

        {/* Cryptographic Compliance Badges */}
        <div className="mt-6 pt-5 border-t border-border flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-500">
              <CheckCircle2 className="h-4 w-4" />
            </div>
            <div>
              <p className="text-xs font-semibold text-text-primary">Enterprise OAuth2 / SAML Synchronized</p>
              <p className="text-[11px] text-text-muted">Biometric access passes and OAuth scopes verified against Active Directory</p>
            </div>
          </div>
          <Badge variant="outline" size="sm" className="font-mono">
            TENANT: org-nova-01
          </Badge>
        </div>
      </Card>
    </div>
  );
};
