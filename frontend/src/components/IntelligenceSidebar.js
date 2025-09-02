import React from "react";
import { MapPin, Sparkles, Wand2, Download, Target, Crown, CheckCircle2, Clock, ArrowLeft, Search, History, LogOut } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const SidebarNavItem = ({ icon: Icon, label, isActive, onClick, status, disabled }) => (
  <button onClick={onClick} disabled={disabled} className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all duration-200 ${disabled ? 'cursor-not-allowed text-neutral-400' : (isActive ? 'bg-blue-100 text-blue-900 border-blue-200' : 'text-neutral-700 hover:bg-neutral-100')}`}> <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-neutral-500'}`} /><span className="font-medium text-sm flex-1">{label}</span>{status === 'complete' && <CheckCircle2 className="w-4 h-4 text-green-600" />}{status === 'processing' && <Clock className="w-4 h-4 text-orange-500" />}</button>
);

const IntelligenceSidebar = ({ 
  analysisData, 
  activeCategory = 'overview', 
  onNavigate, 
  onBackToDashboard, 
  loading = false,
  onShowAnalysisModal,
  onShowPreviousZipsModal
}) => {
  return (
    <div className="w-80 bg-white border-r border-neutral-200 min-h-screen">
      <div className="p-6">
        {activeCategory !== 'overview' && onBackToDashboard && (<button onClick={onBackToDashboard} className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 text-sm mb-4 transition-colors"><ArrowLeft className="w-4 h-4" />Back to Dashboard</button>)}
        <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
          <div className="flex items-center gap-2 mb-2"><Crown className="w-4 h-4 text-blue-600" /><span className="text-xs font-semibold text-blue-800">EXCLUSIVE TERRITORY</span></div>
          <h2 className="text-lg font-bold text-neutral-900">ZIP {analysisData?.zip_code || analysisData?.buyer_migration?.location?.zip_code || '...'}</h2>
          <p className="text-sm text-neutral-600">{analysisData?.buyer_migration?.location?.city}, {analysisData?.buyer_migration?.location?.state}</p>
          <div className="flex items-center gap-2 mt-2 text-xs text-green-700"><CheckCircle2 className="w-3 h-3" /><span>{loading ? 'Analysis in progress' : 'License Active • 6 months remaining'}</span></div>
        </div>
        <div className="space-y-1">
          <SidebarNavItem icon={Target} label="Intelligence Overview" isActive={activeCategory === 'overview'} onClick={() => onNavigate && onNavigate('overview', 'Intelligence Overview', null)} status={loading ? 'processing' : 'complete'} disabled={false} />
          <div className="pt-3 pb-2"><p className="text-xs font-semibold text-neutral-500 uppercase tracking-wide px-3">Intelligence Categories</p></div>
          <SidebarNavItem icon={MapPin} label="Buyer Migration Intel" isActive={activeCategory === 'buyer_migration'} onClick={() => onNavigate && onNavigate('detail', 'Buyer Migration Intel', { key: 'buyer_migration', data: analysisData?.buyer_migration })} status={loading ? 'processing' : 'complete'} disabled={loading} />
          <SidebarNavItem icon={Sparkles} label="SEO & YouTube Trends" isActive={activeCategory === 'seo_youtube_trends'} onClick={() => onNavigate && onNavigate('detail', 'SEO & YouTube Trends', { key: 'seo_youtube_trends', data: analysisData?.seo_youtube_trends })} status={loading ? 'processing' : 'complete'} disabled={loading} />
          <SidebarNavItem icon={Wand2} label="Content Strategy" isActive={activeCategory === 'content_strategy'} onClick={() => onNavigate && onNavigate('detail', 'Content Strategy', { key: 'content_strategy', data: analysisData?.content_strategy })} status={loading ? 'processing' : 'complete'} disabled={loading} />
          <SidebarNavItem icon={Download} label="Content Assets" isActive={activeCategory === 'content_assets'} onClick={() => onNavigate && onNavigate('detail', 'Content Assets', { key: 'content_assets', data: analysisData?.content_assets })} status={loading ? 'processing' : 'complete'} disabled={loading} />
          
          {/* New Testing Section */}
          <div className="pt-4 pb-2"><p className="text-xs font-semibold text-neutral-500 uppercase tracking-wide px-3">Testing Tools</p></div>
          <SidebarNavItem 
            icon={Search} 
            label="ZIP Code Analysis" 
            isActive={false} 
            onClick={() => onShowAnalysisModal && onShowAnalysisModal()} 
            disabled={false} 
          />
          <SidebarNavItem 
            icon={History} 
            label="Previous ZIP Codes" 
            isActive={false} 
            onClick={() => onShowPreviousZipsModal && onShowPreviousZipsModal()} 
            disabled={false} 
          />
        </div>
      </div>
    </div>
  );
};

export default IntelligenceSidebar;