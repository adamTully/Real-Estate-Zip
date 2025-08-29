import React, { useState } from "react";
import { Calendar, Video, FileText, Mail, Target, Lightbulb, Users, TrendingUp, CheckCircle2 } from "lucide-react";

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

const WeekCard = ({ week, theme, shortForm, longForm, leadMagnet, emailTheme, isActive, onClick }) => (
  <Card 
    className={`p-5 cursor-pointer transition-all duration-200 hover:shadow-md ${
      isActive ? 'ring-2 ring-blue-500 shadow-md' : ''
    }`}
    onClick={onClick}
  >
    <div className="space-y-4">
      {/* Week Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
            isActive ? 'bg-blue-500 text-white' : 'bg-neutral-100 text-neutral-600'
          }`}>
            {week}
          </div>
          <h3 className="font-semibold text-lg text-neutral-900">{theme}</h3>
        </div>
        {isActive && <CheckCircle2 className="w-5 h-5 text-blue-500" />}
      </div>

      {/* Content Preview */}
      <div className="space-y-3 text-sm">
        <div className="flex items-start gap-2">
          <Video className="w-4 h-4 text-red-500 mt-1 flex-shrink-0" />
          <p className="text-neutral-700 leading-relaxed line-clamp-2">
            {shortForm.length > 100 ? shortForm.substring(0, 100) + '...' : shortForm}
          </p>
        </div>
        
        <div className="flex items-start gap-2">
          <FileText className="w-4 h-4 text-blue-500 mt-1 flex-shrink-0" />
          <p className="text-neutral-700 leading-relaxed line-clamp-2">
            {longForm.length > 100 ? longForm.substring(0, 100) + '...' : longForm}
          </p>
        </div>
      </div>

      {/* Expand Indicator */}
      <div className="text-xs text-neutral-500 text-center pt-2 border-t border-neutral-100">
        {isActive ? 'Click to collapse' : 'Click to expand details'}
      </div>
    </div>
  </Card>
);

const WeekDetailView = ({ weekData }) => (
  <ContentBlock className="space-y-6">
    <div className="flex items-center gap-3 pb-3 border-b border-neutral-100">
      <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
        {weekData.week}
      </div>
      <h3 className="text-xl font-semibold text-neutral-900">Week {weekData.week}: {weekData.theme}</h3>
    </div>

    {/* Short-form Content */}
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Video className="w-5 h-5 text-red-500" />
        <h4 className="font-semibold text-neutral-900">Short-form Content (IG/TikTok/YouTube Shorts)</h4>
      </div>
      <div className="bg-red-50 p-4 rounded-lg border-l-4 border-l-red-400">
        <p className="text-red-900 leading-relaxed">{weekData.short_form}</p>
      </div>
    </div>

    {/* Long-form Content */}
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <FileText className="w-5 h-5 text-blue-500" />
        <h4 className="font-semibold text-neutral-900">Long-form Content (YouTube/Blog/Podcast)</h4>
      </div>
      <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-l-blue-400">
        <p className="text-blue-900 leading-relaxed">{weekData.long_form}</p>
      </div>
    </div>

    {/* Lead Magnet */}
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Target className="w-5 h-5 text-green-500" />
        <h4 className="font-semibold text-neutral-900">Lead Magnet & CTA</h4>
      </div>
      <div className="bg-green-50 p-4 rounded-lg border-l-4 border-l-green-400">
        <p className="text-green-900 leading-relaxed">{weekData.lead_magnet}</p>
      </div>
    </div>

    {/* Email Theme */}
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Mail className="w-5 h-5 text-purple-500" />
        <h4 className="font-semibold text-neutral-900">Email & Retargeting Theme</h4>
      </div>
      <div className="bg-purple-50 p-4 rounded-lg border-l-4 border-l-purple-400">
        <p className="text-purple-900 leading-relaxed">{weekData.email_theme}</p>
      </div>
    </div>
  </ContentBlock>
);

const StrategyInsight = ({ category, recommendation }) => (
  <div className="bg-gradient-to-r from-orange-50 to-yellow-50 p-4 rounded-lg border-l-4 border-l-orange-400">
    <h4 className="font-semibold text-orange-900 mb-2">{category}</h4>
    <p className="text-orange-800 text-sm leading-relaxed">{recommendation}</p>
  </div>
);

const ContentStrategyDetail = ({ data }) => {
  const [activeWeek, setActiveWeek] = useState(1);

  if (!data) return null;

  const currentWeek = data.weekly_roadmap?.find(week => week.week === activeWeek);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-neutral-900">
          Content Marketing Strategy
        </h1>
        <div className="flex items-center justify-center gap-2 text-neutral-600">
          <Calendar className="w-4 h-4" />
          <span className="text-lg">
            8-Week Roadmap for {data.location?.city}, {data.location?.state}
          </span>
        </div>
        <p className="text-neutral-600 max-w-2xl mx-auto leading-relaxed">
          Comprehensive multi-channel marketing strategy to attract buyers relocating to your market.
        </p>
      </div>

      {/* Success Metrics Overview */}
      {data.success_metrics && (
        <ContentBlock className="bg-gradient-to-r from-neutral-50 to-blue-50 border-blue-200">
          <div className="flex items-start gap-3">
            <TrendingUp className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-3">Strategy Goals</h3>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-medium text-blue-900 mb-1">Content Goals:</p>
                  <p className="text-blue-800 leading-relaxed">{data.success_metrics.content_goals}</p>
                </div>
                <div>
                  <p className="font-medium text-blue-900 mb-1">Lead Generation:</p>
                  <p className="text-blue-800 leading-relaxed">{data.success_metrics.lead_generation}</p>
                </div>
              </div>
            </div>
          </div>
        </ContentBlock>
      )}

      {/* 8-Week Roadmap */}
      {data.weekly_roadmap && (
        <Section title="8-Week Content Roadmap" icon={Calendar}>
          {/* Week Navigation */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            {data.weekly_roadmap.map((week) => (
              <WeekCard
                key={week.week}
                week={week.week}
                theme={week.theme}
                shortForm={week.short_form}
                longForm={week.long_form}
                leadMagnet={week.lead_magnet}
                emailTheme={week.email_theme}
                isActive={activeWeek === week.week}
                onClick={() => setActiveWeek(week.week)}
              />
            ))}
          </div>

          {/* Active Week Details */}
          {currentWeek && <WeekDetailView weekData={currentWeek} />}
        </Section>
      )}

      {/* Implementation Strategy */}
      {data.implementation_strategy && (
        <Section title="Implementation Strategy & Best Practices" icon={Lightbulb}>
          <div className="space-y-4">
            {data.implementation_strategy.map((insight, index) => (
              <StrategyInsight
                key={index}
                category={insight.category}
                recommendation={insight.recommendation}
              />
            ))}
          </div>
        </Section>
      )}

      {/* Quick Reference Guide */}
      <ContentBlock className="bg-gradient-to-r from-neutral-50 to-green-50 border-green-200">
        <div className="flex items-start gap-3">
          <Users className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-3">Execution Checklist</h3>
            <div className="space-y-2 text-sm text-green-800">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Schedule all 8 weeks of content in advance using the roadmap</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Set up lead magnet landing pages and email sequences for each week</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Create retargeting audiences for each content type and theme</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Track engagement metrics and adjust content based on performance</span>
              </div>
            </div>
          </div>
        </div>
      </ContentBlock>
    </div>
  );
};

export default ContentStrategyDetail;