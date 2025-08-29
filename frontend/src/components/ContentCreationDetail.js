import React, { useState } from "react";
import { FileText, Download, Mail, BarChart3, Video, Calendar, CheckCircle2, FolderOpen } from "lucide-react";

// Reusable UI components
const Card = ({ className = "", children, ...props }) => (
  <div className={`rounded-2xl shadow-sm border border-neutral-200 bg-white ${className}`} {...props}>
    {children}
  </div>
);

const Section = ({ title, icon: Icon, children, className = "" }) => (
  <div className={`space-y-4 ${className}`}>
    <div className="flex items-center gap-3 pb-2 border-b border-neutral-100">
      {Icon && <Icon className="w-5 h-5 text-neutral-600" />}
      <h2 className="text-xl font-semibold text-neutral-900">{title}</h2>
    </div>
    {children}
  </div>
);

const ContentBlock = ({ children, className = "" }) => (
  <div className={`bg-white rounded-xl p-6 border border-neutral-200 shadow-sm ${className}`}>
    {children}
  </div>
);

const DownloadCard = ({ title, description, fileType, fileSize, onDownload, icon: Icon }) => (
  <Card className="p-4 hover:shadow-md transition-all duration-200 group">
    <div className="space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
            <Icon className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-neutral-900">{title}</h3>
            <p className="text-sm text-neutral-600">{fileType} • {fileSize}</p>
          </div>
        </div>
      </div>
      
      <p className="text-sm text-neutral-700 leading-relaxed">
        {description}
      </p>
      
      <button
        onClick={onDownload}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Download className="w-4 h-4" />
        Download {fileType}
      </button>
    </div>
  </Card>
);

const ContentLibrarySection = ({ title, description, items, icon: Icon }) => {
  const [downloadStatus, setDownloadStatus] = useState({});

  const handleDownload = async (itemName, content, fileType) => {
    setDownloadStatus(prev => ({ ...prev, [itemName]: 'downloading' }));
    
    // Simulate download delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Create and download file
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = itemName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    setDownloadStatus(prev => ({ ...prev, [itemName]: 'completed' }));
    
    // Reset status after 3 seconds
    setTimeout(() => {
      setDownloadStatus(prev => ({ ...prev, [itemName]: null }));
    }, 3000);
  };

  return (
    <Section title={title} icon={Icon}>
      <ContentBlock>
        <p className="text-neutral-700 mb-6 leading-relaxed">
          {description}
        </p>
      </ContentBlock>
      
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((item, index) => {
          const status = downloadStatus[item.name];
          
          return (
            <Card key={index} className="p-4 hover:shadow-md transition-shadow">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-neutral-900 text-sm leading-tight">
                    {item.title || item.name}
                  </h4>
                  {status === 'completed' && (
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                  )}
                </div>
                
                <p className="text-xs text-neutral-600">
                  {item.fileType} • Est. {item.estimatedSize}
                </p>
                
                <p className="text-xs text-neutral-700 leading-relaxed">
                  {item.description}
                </p>
                
                <button
                  onClick={() => handleDownload(item.name, item.content, item.fileType)}
                  disabled={status === 'downloading'}
                  className={`w-full flex items-center justify-center gap-2 px-3 py-2 text-xs rounded-lg transition-colors ${
                    status === 'downloading'
                      ? 'bg-neutral-100 text-neutral-500 cursor-not-allowed'
                      : status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
                  }`}
                >
                  {status === 'downloading' ? (
                    <>
                      <div className="w-3 h-3 border-2 border-neutral-400 border-t-transparent rounded-full animate-spin" />
                      Downloading...
                    </>
                  ) : status === 'completed' ? (
                    <>
                      <CheckCircle2 className="w-3 h-3" />
                      Downloaded
                    </>
                  ) : (
                    <>
                      <Download className="w-3 h-3" />
                      Download
                    </>
                  )}
                </button>
              </div>
            </Card>
          );
        })}
      </div>
    </Section>
  );
};

const ContentCreationDetail = ({ data }) => {
  if (!data) return null;

  // Generate sample blog posts based on SEO findings
  const blogPosts = Array.from({ length: 10 }, (_, i) => ({
    name: `${data.location?.city?.toLowerCase().replace(' ', '-')}-blog-post-${i + 1}.md`,
    title: `Blog Post ${i + 1}: ${[
      `Is ${data.location?.city} a Good Place to Live? Complete 2025 Guide`,
      `${data.location?.city} Cost of Living vs Major Cities`,
      `Best Neighborhoods in ${data.location?.city} for Families`,
      `Moving to ${data.location?.city}: What You Need to Know`,
      `${data.location?.city} Schools Guide: Rankings and Districts`,
      `Things to Do in ${data.location?.city}: Local's Guide`,
      `${data.location?.city} Real Estate Market 2025 Analysis`,
      `Renting vs Buying in ${data.location?.city}`,
      `${data.location?.city} Safety Guide: Crime Stats and Best Areas`,
      `Why Remote Workers Choose ${data.location?.city}`
    ][i]}`,
    fileType: 'Markdown',
    estimatedSize: `${Math.floor(Math.random() * 3) + 2}KB`,
    description: `SEO-optimized blog post targeting long-tail keywords and local search intent for ${data.location?.city}.`,
    content: `# ${[
      `Is ${data.location?.city} a Good Place to Live? Complete 2025 Guide`,
      `${data.location?.city} Cost of Living vs Major Cities`,
      `Best Neighborhoods in ${data.location?.city} for Families`
    ][i % 3]}

## Introduction
[Content optimized for ${data.location?.city} market...]

## Key Points
- Local market insights
- Neighborhood analysis  
- Cost comparisons
- Quality of life factors

## Conclusion
[Call-to-action for real estate services...]`
  }));

  // Generate lead magnets based on content strategy
  const leadMagnets = [
    {
      name: `${data.location?.city?.toLowerCase().replace(' ', '-')}-cost-living-guide.pdf`,
      title: `${data.location?.city} Cost of Living & Tax Comparison Guide`,
      fileType: 'PDF',
      estimatedSize: '1.2MB',
      description: 'Comprehensive guide comparing housing costs, taxes, and salary requirements.',
      content: `${data.location?.city} Cost of Living Guide\n\nDetailed comparison of living costs...\n\n[Generated PDF content]`
    },
    {
      name: `${data.location?.city?.toLowerCase().replace(' ', '-')}-neighborhood-matcher.pdf`,
      title: `${data.location?.city} Neighborhood Matcher Report`,
      fileType: 'PDF', 
      estimatedSize: '980KB',
      description: 'Interactive quiz results with personalized neighborhood recommendations.',
      content: `Neighborhood Recommendations for ${data.location?.city}\n\n[Personalized results based on quiz responses]`
    },
    {
      name: `${data.location?.city?.toLowerCase().replace(' ', '-')}-family-checklist.pdf`,
      title: 'Family Relocation Checklist',
      fileType: 'PDF',
      estimatedSize: '756KB', 
      description: 'School comparison charts, enrollment tips, and family resources.',
      content: `Family Relocation Checklist for ${data.location?.city}\n\n[Comprehensive family-focused moving guide]`
    },
    {
      name: `${data.location?.city?.toLowerCase().replace(' ', '-')}-buyer-toolkit.pdf`,
      title: 'Home Buyer Toolkit',
      fileType: 'PDF',
      estimatedSize: '1.1MB',
      description: 'Pre-approval checklist, timeline, and local lender contacts.',
      content: `${data.location?.city} Home Buyer's Toolkit\n\n[Complete buyer resources and checklists]`
    },
    {
      name: `${data.location?.city?.toLowerCase().replace(' ', '-')}-remote-work-guide.pdf`,
      title: 'Remote Work Relocation Guide',
      fileType: 'PDF',
      estimatedSize: '890KB',
      description: 'Cost calculators, home office setup tips, and tax deductions.',
      content: `Remote Work Guide for ${data.location?.city}\n\n[Remote work relocation strategies and resources]`
    },
    {
      name: `${data.location?.city?.toLowerCase().replace(' ', '-')}-rental-report.pdf`,
      title: 'Rental Market Report',
      fileType: 'PDF',
      estimatedSize: '1.3MB',
      description: 'Rent trends, ROI calculators, and investment analysis.',
      content: `${data.location?.city} Rental Market Analysis\n\n[Investment and rental market insights]`
    },
    {
      name: `${data.location?.city?.toLowerCase().replace(' ', '-')}-relocation-planner.xlsx`,
      title: 'Relocation Planner Spreadsheet',
      fileType: 'Excel',
      estimatedSize: '124KB',
      description: 'Budget template for moving costs, travel, and closing expenses.',
      content: `Relocation Planning Spreadsheet for ${data.location?.city}\n\n[Excel template with formulas and checklists]`
    },
    {
      name: `${data.location?.city?.toLowerCase().replace(' ', '-')}-community-calendar.pdf`,
      title: 'Community Calendar',
      fileType: 'PDF',
      estimatedSize: '645KB',
      description: 'Monthly events, festivals, and local activities throughout the year.',
      content: `${data.location?.city} Community Events Calendar\n\n[Year-round local events and activities]`
    }
  ];

  // Generate email campaigns
  const emailCampaigns = Array.from({ length: 8 }, (_, i) => ({
    name: `${data.location?.city?.toLowerCase().replace(' ', '-')}-email-week-${i + 1}.html`,
    title: `Week ${i + 1} Email Campaign: ${[
      'Welcome + Savings',
      'Find Your Fit', 
      'Family Focus',
      'Market Insider',
      'Remote Work Ready',
      'Rent vs Buy',
      'Your Move Simplified',
      'Stay Connected'
    ][i]}`,
    fileType: 'HTML',
    estimatedSize: `${Math.floor(Math.random() * 8) + 4}KB`,
    description: `Email sequence for week ${i + 1} of the content strategy roadmap.`,
    content: `Subject: Week ${i + 1} - ${data.location?.city} Market Update

Hi [First Name],

[Week ${i + 1} email content optimized for ${data.location?.city} market...]

Best regards,
[Your Name]`
  }));

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-neutral-900">
          Content Creation Library
        </h1>
        <div className="flex items-center justify-center gap-2 text-neutral-600">
          <FolderOpen className="w-4 h-4" />
          <span className="text-lg">
            Ready-to-Use Content for {data.location?.city}, {data.location?.state}
          </span>
        </div>
        <p className="text-neutral-600 max-w-2xl mx-auto leading-relaxed">
          Download production-ready blog posts, lead magnets, and email campaigns based on your market intelligence findings.
        </p>
      </div>

      {/* Content Overview */}
      <ContentBlock className="bg-gradient-to-r from-neutral-50 to-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <PresentationChart className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">Content Library Overview</h3>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-600" />
                <span className="text-blue-800"><strong>10 Blog Posts</strong> • SEO-optimized articles</span>
              </div>
              <div className="flex items-center gap-2">
                <PresentationChart className="w-4 h-4 text-green-600" />
                <span className="text-green-800"><strong>8 Lead Magnets</strong> • High-converting PDFs</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-purple-600" />
                <span className="text-purple-800"><strong>8 Email Campaigns</strong> • Weekly sequences</span>
              </div>
            </div>
          </div>
        </div>
      </ContentBlock>

      {/* Blog Posts Section */}
      <ContentLibrarySection
        title="SEO-Optimized Blog Posts"
        description="Ten full-length blog articles targeting your market's most searched keywords and questions. Each post is optimized for local SEO and includes clear calls-to-action for lead generation."
        items={blogPosts}
        icon={FileText}
      />

      {/* Lead Magnets Section */}
      <ContentLibrarySection
        title="Lead Magnets & Gated Content"
        description="High-converting lead magnets based on your 8-week content strategy. Each PDF is designed to capture leads at different stages of the buyer journey."
        items={leadMagnets}
        icon={PresentationChart}
      />

      {/* Email Campaigns Section */}
      <ContentLibrarySection
        title="Email Marketing Campaigns"
        description="Ready-to-send email sequences that correspond to your weekly content roadmap. Each email includes subject lines, content, and clear calls-to-action."
        items={emailCampaigns}
        icon={Mail}
      />

      {/* Usage Guidelines */}
      <ContentBlock className="bg-gradient-to-r from-neutral-50 to-green-50 border-green-200">
        <div className="flex items-start gap-3">
          <Video className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-3">Usage Guidelines</h3>
            <div className="space-y-2 text-sm text-green-800">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Customize content with your branding, contact info, and local insights</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Schedule blog posts and emails according to your content strategy timeline</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Set up lead magnet landing pages with your email marketing platform</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Track performance metrics and adjust content based on engagement data</span>
              </div>
            </div>
          </div>
        </div>
      </ContentBlock>
    </div>
  );
};

export default ContentCreationDetail;