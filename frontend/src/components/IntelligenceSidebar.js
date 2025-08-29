import React from "react";
import { 
  MapPin, 
  Sparkles, 
  Wand2, 
  FileText, 
  Download,
  Target,
  Crown,
  CheckCircle2,
  Clock,
  ArrowLeft
} from "lucide-react";

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

const IntelligenceSidebar = ({ 
  analysisData, 
  activeCategory = 'overview', 
  onNavigate, 
  onBackToDashboard 
}) => {
  if (!analysisData) return null;

  const categories = [
    {
      id: 'buyer_migration',
      title: 'Buyer Migration Intel',
      icon: MapPin,
      data: analysisData.buyer_migration,
      status: 'complete'
    },
    {
      id: 'seo_youtube_trends', 
      title: 'SEO & YouTube Trends',
      icon: Sparkles,
      data: analysisData.seo_youtube_trends,
      status: 'complete'
    },
    {
      id: 'content_strategy',
      title: 'Content Strategy', 
      icon: Wand2,
      data: analysisData.content_strategy,
      status: 'complete'
    },
    {
      id: 'hidden_listings',
      title: 'Market Research',
      icon: FileText,
      data: analysisData.hidden_listings,
      status: 'complete'
    },
    {
      id: 'content_assets',
      title: 'Content Creation',
      icon: Download, 
      data: analysisData.content_assets,
      status: 'complete'
    }
  ];

  return (
    <div className="w-80 bg-white border-r border-neutral-200 min-h-screen">
      <div className="p-6">
        {/* Back to Dashboard Button */}
        {activeCategory !== 'overview' && onBackToDashboard && (
          <button
            onClick={onBackToDashboard}
            className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 text-sm mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </button>
        )}

        {/* Territory Header */}
        <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
          <div className="flex items-center gap-2 mb-2">
            <Crown className="w-4 h-4 text-blue-600" />
            <span className="text-xs font-semibold text-blue-800">EXCLUSIVE TERRITORY</span>
          </div>
          <h2 className="text-lg font-bold text-neutral-900">
            ZIP {analysisData.zip_code || analysisData.buyer_migration?.location?.zip_code}
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
            onClick={() => onNavigate('overview', 'Intelligence Overview', null)}
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
              onClick={() => onNavigate('detail', category.title, { key: category.id, data: category.data })}
              status={category.status}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default IntelligenceSidebar;