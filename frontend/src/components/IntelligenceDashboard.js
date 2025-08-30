import React from "react";
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
  Calendar,
  Target
} from "lucide-react";
import IntelligenceSidebar from "./IntelligenceSidebar";

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

const ProgressBar = ({ percent = 0 }) => (
  <div className="w-full h-2 bg-neutral-100 rounded-full overflow-hidden">
    <div className="h-2 bg-blue-600 transition-all" style={{ width: `${percent}%` }} />
  </div>
);

const Skeleton = ({ className = "" }) => (
  <div className={`animate-pulse bg-neutral-100 rounded ${className}`} />
);

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
  isActive,
  loading = false,
  task = null
}) => (
  <Card className={`p-6 transition-all duration-200 ${isActive ? 'ring-2 ring-blue-500' : ''}`}>
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
          {!loading && status === 'complete' && (
            <Badge variant="success">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              Complete
            </Badge>
          )}
          {loading && (
            <Badge variant="warning">
              <Clock className="w-3 h-3 mr-1" />
              Processing
            </Badge>
          )}
        </div>
      </div>

      {/* Loading State with Task Progress */}
      {loading ? (
        <div className="space-y-4">
          {task && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-neutral-600">
                <span>{task.title}</span>
                <span>{task.percent}%</span>
              </div>
              <ProgressBar percent={task.percent} />
            </div>
          )}
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-5/6" />
          <div className="flex items-center justify-between pt-2 border-t border-neutral-100">
            <button
              disabled
              className="flex items-center gap-2 text-neutral-400 text-sm font-medium cursor-not-allowed"
            >
              View Full Analysis
              <ExternalLink className="w-3 h-3" />
            </button>
            <button
              disabled
              className="px-3 py-1 bg-neutral-100 text-neutral-400 text-xs rounded-lg cursor-not-allowed"
            >
              Quick Action
            </button>
          </div>
        </div>
      ) : (
        <>
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
        </>
      )}
    </div>
  </Card>
);

const IntelligenceDashboard = ({ analysisData, onViewDetail, loading = false, taskProgress = {}, overallProgress = 0 }) => {
  const activeCategory = 'overview';

  const categories = [
    {
      id: 'buyer_migration',
      title: 'Buyer Migration Intel',
      description: 'Migration patterns and buyer motivations',
      icon: MapPin,
      data: analysisData?.buyer_migration,
      status: 'complete'
    },
    {
      id: 'seo_youtube_trends', 
      title: 'SEO & YouTube Trends',
      description: 'Keyword research and content opportunities',
      icon: Sparkles,
      data: analysisData?.seo_youtube_trends,
      status: 'complete'
    },
    {
      id: 'content_strategy',
      title: 'Content Strategy', 
      description: '8-week marketing roadmap',
      icon: Wand2,
      data: analysisData?.content_strategy,
      status: 'complete'
    },
    {
      id: 'hidden_listings',
      title: 'Market Research',
      description: 'Hidden opportunities and seller profiles', 
      icon: FileText,
      data: analysisData?.hidden_listings,
      status: 'complete'
    },
    {
      id: 'content_assets',
      title: 'Content Creation',
      description: 'Downloadable marketing materials',
      icon: Download, 
      data: analysisData?.content_assets,
      status: 'complete'
    }
  ];

  const getPreviewData = (category, data) => {
    if (!data) return null;
    switch (category.id) {
      case 'buyer_migration':
        return [data?.summary];
      case 'seo_youtube_trends':
        return [data?.summary];
      case 'content_strategy':
        return [data?.summary];
      case 'hidden_listings':
        return [data?.summary];
      case 'content_assets':
        return [data?.summary];
      default:
        return [];
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100">
      <div className="flex">
        {/* Sidebar Navigation */}
        <IntelligenceSidebar
          analysisData={analysisData}
          activeCategory={activeCategory}
          loading={loading}
          onNavigate={() => {}}
        />

        {/* Main Content Area */}
        <div className="flex-1 p-8 space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-neutral-900 mb-2">
              Market Intelligence Dashboard
            </h1>
            <p className="text-neutral-600">
              {analysisData?.buyer_migration?.location?.city && analysisData?.buyer_migration?.location?.state
                ? `Complete territorial intelligence for ${analysisData.buyer_migration.location.city}, ${analysisData.buyer_migration.location.state}`
                : 'Generating intelligence for your territory...'}
            </p>
          </div>

          {/* Overall Progress */}
          {loading && (
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-neutral-700">Overall Progress</p>
                <p className="text-sm text-neutral-600">{overallProgress}%</p>
              </div>
              <ProgressBar percent={overallProgress} />
            </Card>
          )}

          {/* Tasks Readout */}
          {loading && (
            <div className="grid md:grid-cols-2 gap-4">
              {Object.keys(taskProgress).map((key) => (
                <Card key={key} className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-neutral-800">{taskProgress[key].title}</p>
                    <Badge variant={taskProgress[key].status === 'done' ? 'success' : 'warning'}>
                      {taskProgress[key].status === 'done' ? 'Done' : taskProgress[key].status === 'running' ? 'In Progress' : 'Pending'}
                    </Badge>
                  </div>
                  <ProgressBar percent={taskProgress[key].percent} />
                </Card>
              ))}
            </div>
          )}

          {/* Intelligence Cards Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {categories.map((category) => (
              <IntelligenceCard
                key={category.id}
                category={category.id}
                title={category.title}
                description={category.description}
                summary={!loading ? category.data?.summary : undefined}
                status={category.status}
                previewData={!loading ? getPreviewData(category, category.data) : undefined}
                onViewDetails={() => onViewDetail && onViewDetail(category.id, category.title, category.data)}
                icon={category.icon}
                isActive={false}
                loading={loading}
                task={loading ? taskProgress[category.id] : null}
              />
            ))}
          </div>

          {!loading && (
            // Next Steps
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
          )}
        </div>
      </div>
    </div>
  );
};

export default IntelligenceDashboard;