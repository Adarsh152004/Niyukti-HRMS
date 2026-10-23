import { InquiryModel } from '../models/Inquiry.mjs';
import { getDBStatus } from '../config/db.mjs';

const inMemoryInquiries = [];

export async function submitInquiry(req, res) {
  try {
    const {
      fullName,
      email,
      company,
      role,
      projectType,
      budgetTier,
      timeline,
      projectSummary,
      slackConnect
    } = req.body;

    if (!fullName || !fullName.trim()) {
      return res.status(400).json({ success: false, error: 'Full name is required.' });
    }
    if (!email || !email.includes('@')) {
      return res.status(400).json({ success: false, error: 'Valid company/business email is required.' });
    }
    if (!company || !company.trim()) {
      return res.status(400).json({ success: false, error: 'Company / Organization name is required.' });
    }
    if (!projectSummary || !projectSummary.trim()) {
      return res.status(400).json({ success: false, error: 'Project brief / problem summary is required.' });
    }

    const randomSuffix = Math.floor(10000 + Math.random() * 90000);
    const referenceId = `AZY-INQ-${randomSuffix}`;

    const inquiryPayload = {
      referenceId,
      fullName: fullName.trim(),
      email: email.trim().toLowerCase(),
      company: company.trim(),
      role: role ? role.trim() : undefined,
      projectType: projectType || 'Web Application & SaaS',
      budgetTier: budgetTier || '$50,000 – $100,000',
      timeline: timeline || '2 – 4 Months',
      projectSummary: projectSummary.trim(),
      slackConnect: Boolean(slackConnect),
      status: 'pending_review',
      ndaSigned: true,
      createdAt: new Date(),
    };

    const dbStatus = getDBStatus();
    let savedDoc;

    if (dbStatus.connected) {
      savedDoc = await InquiryModel.create(inquiryPayload);
    } else {
      savedDoc = { ...inquiryPayload, _id: `mem_${Date.now()}` };
      inMemoryInquiries.push(savedDoc);
    }

    console.log(`[InquiryController] ✅ New client discovery inquiry: ${referenceId} (${company} - ${projectType})`);

    return res.status(201).json({
      success: true,
      message: 'Project discovery brief received and registered under bilateral NDA.',
      data: {
        referenceId: savedDoc.referenceId,
        company: savedDoc.company,
        projectType: savedDoc.projectType,
        status: savedDoc.status,
        slaResponseTime: '< 24 Business Hours',
        assignedPrincipal: 'Lead Systems Architect & Engagement Director',
        submittedAt: savedDoc.createdAt,
      },
      meta: {
        storage: dbStatus.connected ? 'mongodb_atlas' : 'resilient_cache',
      }
    });

  } catch (error) {
    console.error('[InquiryController] Error processing inquiry:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to register project inquiry',
      message: error.message,
    });
  }
}

export async function getInquiries(req, res) {
  try {
    const dbStatus = getDBStatus();
    let inquiries;

    if (dbStatus.connected) {
      inquiries = await InquiryModel.find().sort({ createdAt: -1 });
    } else {
      inquiries = [...inMemoryInquiries];
    }

    return res.status(200).json({
      success: true,
      count: inquiries.length,
      data: inquiries,
    });
  } catch (error) {
    console.error('[InquiryController] Error listing inquiries:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to retrieve project inquiries',
      message: error.message,
    });
  }
}
