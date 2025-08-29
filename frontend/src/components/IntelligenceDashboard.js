import React, { useState } from "react";
import { 
  MapPin, 
  Sparkles, 
  Wand2, 
  FileText, 
  Download, 
  ExternalLink, 
  CheckCircle2,
  Clock,
  ArrowRight,
  Crown,
  Calendar,
  Target
} from "lucide-react";

// UI Components
const Card = ({ className = "", children, ...props }) => (
  <div className={`rounded-2xl shadow-sm border border-neutral-200 bg-white ${className}`} {...props}>
    {children}
  </div>
);

const Badge = ({ children, variant = "default" }) => {
  const variants = {
    default: "bg-neutral-100 text-neutral-800",
    success: "bg-green-100 text-green-800",
    warning: "bg-orange-100 text-orange-800",
    info: "bg-blue-100 text-blue-800"
  };
  
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${variants[variant]}`}>
      {children}
    </span>
  );
};

const IntelligenceCard = ({ 
  category, 
  title, 
  description, 
  summary, 
  status, 
  previewData, 
  onViewDetails, 
  onQuickAction,
  icon: Icon,
  isActive 
}) => (
  <Card className={`p-6 hover:shadow-md transition-all duration-200 ${isActive ? 'ring-2 ring-blue-500' : ''}`}>
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Icon className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-lg text-neutral-900">{title}</h3>
            <p className="text-sm text-neutral-600">{description}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {status === 'complete' && (
            <Badge variant="success">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              Complete
            </Badge>
          )}
          {status === 'processing' && (
            <Badge variant="warning">
              <Clock className="w-3 h-3 mr-1" />
              Processing
            </Badge>
          )}
        </div>
      </div>

      {/* Summary */}
      {summary && (
        <div className="bg-neutral-50 p-3 rounded-lg">
          <p className="text-sm text-neutral-700 leading-relaxed">{summary}</p>
        </div>
      )}

      {/* Preview Data */}
      {previewData && (
        <div className="space-y-2">
          {previewData.map((item, index) => (
            <div key={index} className="flex items-center gap-2 text-sm text-neutral-600">
              <span className="w-1 h-1 bg-blue-500 rounded-full"></span>
              <span>{item}</span>
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between pt-2 border-t border-neutral-100">
        <button
          onClick={onViewDetails}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors"
        >
          View Full Analysis
          <ExternalLink className="w-3 h-3" />
        </button>
        
        {onQuickAction && (
          <button
            onClick={onQuickAction}
            className="px-3 py-1 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors"
          >
            Quick Action
          </button>
        )}
      </div>
    </div>
  </Card>
);

const SidebarNavItem = ({ icon: Icon, label, isActive, onClick, status }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all duration-200 ${
      isActive 
        ? 'bg-blue-100 text-blue-900 border-blue-200' 
        : 'text-neutral-700 hover:bg-neutral-100'
    }`}
  >
    <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-neutral-500'}`} />
    <span className="font-medium text-sm flex-1">{label}</span>
    {status === 'complete' && <CheckCircle2 className="w-4 h-4 text-green-600" />}
    {status === 'processing' && <Clock className="w-4 h-4 text-orange-500" />}
  </button>
);

const IntelligenceDashboard = ({ analysisData, onViewDetail }) => {
  const [activeCategory, setActiveCategory] = useState('overview');

  if (!analysisData) return null;

  const categories = [
    {
      id: 'buyer_migration',
      title: 'Buyer Migration Intel',
      description: 'Migration patterns and buyer motivations',
      icon: MapPin,
      data: analysisData.buyer_migration,
      status: 'complete'
    },
    {
      id: 'seo_youtube_trends', 
      title: 'SEO & YouTube Trends',
      description: 'Keyword research and content opportunities',
      icon: Sparkles,
      data: analysisData.seo_youtube_trends,
      status: 'complete'
    },
    {
      id: 'content_strategy',
      title: 'Content Strategy', 
      description: '8-week marketing roadmap',
      icon: Wand2,
      data: analysisData.content_strategy,
      status: 'complete'
    },
    {
      id: 'hidden_listings',
      title: 'Market Research',
      description: 'Hidden opportunities and seller profiles', 
      icon: FileText,
      data: analysisData.hidden_listings,
      status: 'complete'
    },
    {
      id: 'content_assets',
      title: 'Content Creation',
      description: 'Downloadable marketing materials',
      icon: Download, 
      data: analysisData.content_assets,
      status: 'complete'
    }
  ];

  const getPreviewData = (category, data) => {
    switch (category.id) {
      case 'buyer_migration':
        return [
          `Top sources: ${data?.primary_markets?.map(m => m.market).slice(0, 2).join(', ') || 'New York, Los Angeles'}`,
          `Key driver: ${data?.migration_drivers?.[0]?.factor || 'Lower cost of living'}`,
          `${data?.key_metrics?.inbound_buyer_percentage || '45'}% inbound buyers`
        ];
      case 'seo_youtube_trends':
        return [
          `${data?.high_volume_keywords?.length || 8} high-volume keywords identified`,
          `${data?.long_tail_questions?.length || 10} long-tail opportunities`,
          `${data?.video_title_ideas?.length || 8} video content strategies`
        ];
      case 'content_strategy':
        return [
          `8-week multi-channel roadmap`,
          `${data?.weekly_roadmap?.length || 8} weeks of planned content`,
          `Lead magnets, blogs, and email sequences`
        ];
      case 'hidden_listings':
        return [
          `${data?.micro_areas?.length || 4} micro-areas identified`,
          `${data?.seller_profiles?.length || 4} seller profiles analyzed`,
          `${data?.actionable_takeaways?.length || 4} action categories`
        ];
      case 'content_assets':
        return [
          `10 SEO-optimized blog posts`,
          `8 lead magnets and guides`,  
          `8 email campaign templates`
        ];
      default:
        return [];
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100">
      <div className="flex">
        {/* Sidebar Navigation */}
        <div className="w-80 bg-white border-r border-neutral-200 min-h-screen">
          <div className="p-6">
            {/* Territory Header */}
            <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <Crown className="w-4 h-4 text-blue-600" />
                <span className="text-xs font-semibold text-blue-800">EXCLUSIVE TERRITORY</span>
              </div>
              <h2 className="text-lg font-bold text-neutral-900">
                ZIP {analysisData.zip_code}
              </h2>
              <p className="text-sm text-neutral-600">
                {analysisData.buyer_migration?.location?.city}, {analysisData.buyer_migration?.location?.state}
              </p>
              <div className="flex items-center gap-2 mt-2 text-xs text-green-700">
                <CheckCircle2 className="w-3 h-3" />
                <span>License Active • 6 months remaining</span>
              </div>
            </div>

            {/* Navigation Menu */}
            <div className="space-y-1">
              <SidebarNavItem
                icon={Target}
                label="Intelligence Overview"
                isActive={activeCategory === 'overview'}
                onClick={() => setActiveCategory('overview')}
                status="complete"
              />
              
              <div className="pt-3 pb-2">
                <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wide px-3">
                  Intelligence Categories
                </p>
              </div>
              
              {categories.map((category) => (
                <SidebarNavItem
                  key={category.id}
                  icon={category.icon}
                  label={category.title}
                  isActive={activeCategory === category.id}
                  onClick={() => setActiveCategory(category.id)}
                  status={category.status}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 p-8">
          {activeCategory === 'overview' ? (
            // Overview Dashboard
            <div className="space-y-8">
              {/* Header */}
              <div>
                <h1 className="text-3xl font-bold text-neutral-900 mb-2">
                  Market Intelligence Dashboard
                </h1>
                <p className="text-neutral-600">
                  Complete territorial intelligence for {analysisData.buyer_migration?.location?.city}, {analysisData.buyer_migration?.location?.state}
                </p>
              </div>

              {/* Quick Stats */}
              <div className="grid md:grid-cols-4 gap-4">
                <Card className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-50 rounded-lg">
                      <CheckCircle2 className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm text-neutral-600">Completed</p>
                      <p className="text-xl font-bold text-neutral-900">5/5</p>
                    </div>
                  </div>
                </Card>
                
                <Card className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-50 rounded-lg">
                      <FileText className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-neutral-600">Content Pieces</p>
                      <p className="text-xl font-bold text-neutral-900">26</p>
                    </div>
                  </div>
                </Card>
                
                <Card className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-50 rounded-lg">
                      <Sparkles className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-sm text-neutral-600">Keywords Found</p>
                      <p className="text-xl font-bold text-neutral-900">{analysisData.seo_youtube_trends?.high_volume_keywords?.length || 15}</p>
                    </div>
                  </div>
                </Card>
                
                <Card className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-50 rounded-lg">
                      <Calendar className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-sm text-neutral-600">Content Weeks</p>
                      <p className="text-xl font-bold text-neutral-900">8</p>
                    </div>
                  </div>
                </Card>
              </div>

              {/* Intelligence Cards Grid */}
              <div className="grid md:grid-cols-2 gap-6">
                {categories.map((category) => (
                  <IntelligenceCard
                    key={category.id}
                    category={category.id}
                    title={category.title}
                    description={category.description}
                    summary={category.data?.summary}
                    status={category.status}
                    previewData={getPreviewData(category, category.data)}
                    onViewDetails={() => onViewDetail(category.id, category.title, category.data)}
                    icon={category.icon}
                    isActive={false}
                  />
                ))}
              </div>

              {/* Next Steps */}
              <Card className="p-6 bg-gradient-to-r from-neutral-50 to-green-50 border-green-200">
                <div className="flex items-start gap-4">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <ArrowRight className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-neutral-900 mb-2">Recommended Next Steps</h3>
                    <div className="space-y-2 text-sm text-neutral-700">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-600" />
                        <span>Download and customize your content library</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-600" />
                        <span>Begin Week 1 of your content strategy</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-600" />
                        <span>Start prospecting in identified micro-areas</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          ) : (
            // Individual Category View
            <div className="space-y-6">
              {(() => {
                const category = categories.find(c => c.id === activeCategory);
                return (
                  <IntelligenceCard
                    category={category.id}
                    title={category.title}
                    description={category.description}
                    summary={category.data?.summary}
                    status={category.status}
                    previewData={getPreviewData(category, category.data)}
                    onViewDetails={() => onViewDetail(category.id, category.title, category.data)}
                    icon={category.icon}
                    isActive={true}
                  />
                );
              })()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IntelligenceDashboard;