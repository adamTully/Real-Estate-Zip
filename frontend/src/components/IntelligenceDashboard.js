import React from "react";
import { 
  MapPin,
  ExternalLink, 
  CheckCircle2,
  Clock,
  ArrowRight
} from "lucide-react";
import IntelligenceSidebar from "./IntelligenceSidebar";

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
  title, 
  description, 
  summary, 
  onViewDetails, 
  icon: Icon,
  loading = false,
  task = null
}) => (
  <Card className={`p-6 transition-all duration-200`}>
    <div className="space-y-4">
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
          {!loading && (
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
          </div>
        </div>
      ) : (
        <>
          {summary && (
            <div className="bg-neutral-50 p-3 rounded-lg">
              <p className="text-sm text-neutral-700 leading-relaxed">{summary}</p>
            </div>
          )}

          <div className="flex items-center justify-between pt-2 border-t border-neutral-100">
            <button
              onClick={onViewDetails}
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors"
            >
              View Full Analysis
              <ExternalLink className="w-3 h-3" />
            </button>
          </div>
        </>
      )}
    </div>
  </Card>
);

const IntelligenceDashboard = ({ analysisData, onViewDetail, loading = false, taskProgress = {}, overallProgress = 0 }) => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100">
      <div className="flex">
        <IntelligenceSidebar
          analysisData={analysisData}
          activeCategory={'overview'}
          loading={loading}
          onNavigate={() => {}}
        />

        <div className="flex-1 p-8 space-y-8">
          <div>
            <h1 className="text-3xl font-bold text-neutral-900 mb-2">Market Intelligence Dashboard</h1>
            <p className="text-neutral-600">
              {analysisData?.buyer_migration?.location?.city && analysisData?.buyer_migration?.location?.state
                ? `Complete territorial intelligence for ${analysisData.buyer_migration.location.city}, ${analysisData.buyer_migration.location.state}`
                : 'Generating buyer migration intelligence for your territory...'}
            </p>
          </div>

          {loading && (
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-neutral-700">Overall Progress</p>
                <p className="text-sm text-neutral-600">{overallProgress}%</p>
              </div>
              <ProgressBar percent={overallProgress} />
            </Card>
          )}

          {loading && (
            <div className="grid md:grid-cols-1 gap-4">
              {taskProgress.location && (
                <Card className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-neutral-800">{taskProgress.location.title}</p>
                    <Badge variant={taskProgress.location.status === 'done' ? 'success' : 'warning'}>
                      {taskProgress.location.status === 'done' ? 'Done' : 'In Progress'}
                    </Badge>
                  </div>
                  <ProgressBar percent={taskProgress.location.percent} />
                </Card>
              )}
              {taskProgress.buyer_migration && (
                <Card className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-neutral-800">{taskProgress.buyer_migration.title}</p>
                    <Badge variant={taskProgress.buyer_migration.status === 'done' ? 'success' : 'warning'}>
                      {taskProgress.buyer_migration.status === 'done' ? 'Done' : 'In Progress'}
                    </Badge>
                  </div>
                  <ProgressBar percent={taskProgress.buyer_migration.percent} />
                </Card>
              )}
            </div>
          )}

          <div className="grid md:grid-cols-1 gap-6">
            <IntelligenceCard
              title={'Buyer Migration Intel'}
              description={'Migration patterns and buyer motivations'}
              summary={!loading ? analysisData?.buyer_migration?.summary : undefined}
              onViewDetails={() => onViewDetail && onViewDetail('buyer_migration', 'Buyer Migration Intel', analysisData?.buyer_migration)}
              icon={MapPin}
              loading={loading}
              task={loading ? taskProgress.buyer_migration : null}
            />
          </div>

          {!loading && (
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
                      <span>Review Buyer Migration analysis and define content angles</span>
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