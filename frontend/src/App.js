import React, { useState, useMemo, useEffect, useRef } from "react";
import { 
  Loader2, 
  MapPin, 
  Sparkles, 
  Wand2,
  ArrowLeft, 
  ExternalLink,
  AlertCircle,
  CheckCircle2
} from "lucide-react";
import * as Toast from "@radix-ui/react-toast";
import { Routes, Route, useNavigate, useLocation, Navigate } from "react-router-dom";
import BuyerMigrationDetailView from "./components/BuyerMigrationDetail";
import SeoYouTubeDetail from "./components/SeoYouTubeDetail";
import ContentStrategyDetail from "./components/ContentStrategyDetail";
import ContentCreationDetail from "./components/ContentCreationDetail";
import IntelligenceDashboard from "./components/IntelligenceDashboard";
import IntelligenceSidebar from "./components/IntelligenceSidebar";
import axios from "axios";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Card = ({ className = "", children, ...props }) => (
  <div className={`rounded-2xl shadow-lg border border-neutral-200 bg-white ${className}`} {...props}>
    {children}
  </div>
);
const CardContent = ({ className = "", children }) => (<div className={`p-5 md:p-6 ${className}`}>{children}</div>);
const Button = ({ className = "", variant = "default", children, disabled, ...props }) => {
  const baseClasses = "inline-flex items-center justify-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  const variants = { default: "bg-black text-white hover:bg-neutral-800 focus:ring-black disabled:bg-neutral-300", outline: "bg-white text-black border border-neutral-300 hover:bg-neutral-50 focus:ring-neutral-500", ghost: "bg-transparent text-neutral-700 hover:bg-neutral-100 focus:ring-neutral-500" };
  return (<button className={`${baseClasses} ${variants[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`} disabled={disabled} {...props}>{children}</button>);
};
const Input = ({ className = "", error, ...props }) => (<input className={`w-full rounded-xl border px-4 py-3 text-base outline-none focus:ring-4 focus:ring-black/5 ${error ? 'border-red-300 focus:ring-red-100' : 'border-neutral-300'} ${className}`} {...props} />);
const Alert = ({ variant = "default", children }) => { const variants = { default: "bg-blue-50 border-blue-200 text-blue-800", error: "bg-red-50 border-red-200 text-red-800", success: "bg-green-50 border-green-200 text-green-800" }; return (<div className={`p-4 rounded-xl border ${variants[variant]} flex items-start gap-3`}>{variant === "error" && <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />} {variant === "success" && <CheckCircle2 className="w-5 h-5 mt-0.5 flex-shrink-0" />}<div className="text-sm">{children}</div></div>); };

// Five tasks now: location -> buyer -> seo -> content strategy -> assets
const TASK_PLAN = [
  { id: "location", title: "Task 1 - ZIP Code Analysis", range: [0, 15] },
  { id: "buyer_migration", title: "Task 2 - Buyer Migration Intelligence", range: [15, 40] },
  { id: "seo_youtube_trends", title: "Task 3 - SEO & YouTube Trends", range: [40, 70] },
  { id: "content_strategy", title: "Task 4 - Content Strategy", range: [70, 90] },
  { id: "content_assets", title: "Task 5 - Content Assets", range: [90, 100] },
];
function computeTaskProgress(overall) { const progress = {}; TASK_PLAN.forEach((t) => { const [start, end] = t.range; let pct = 0; if (overall >= end) pct = 100; else if (overall <= start) pct = 0; else pct = Math.round(((overall - start) / (end - start)) * 100); const status = pct === 0 ? "pending" : pct === 100 ? "done" : "running"; progress[t.id] = { percent: Math.max(0, Math.min(100, pct)), status, title: t.title }; }); return progress; }

export default function ZipIntelApp() {
  const navigate = useNavigate();
  const location = useLocation();

  const [zip, setZip] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [analysisData, setAnalysisData] = useState(null);
  const [overallProgress, setOverallProgress] = useState(0);
  const [taskProgress, setTaskProgress] = useState({});
  const progressTimerRef = useRef(null);

  useEffect(() => { setTaskProgress(computeTaskProgress(overallProgress)); }, [overallProgress]);

  // Attempt to hydrate analysis from last zip on deep links
  useEffect(() => {
    const lastZip = localStorage.getItem('zipintel:last_zip');
    const onDetailRoute = ["/dashboard","/market-intelligence","/seo-youtube-trends","/content-strategy","/content-assets"].includes(location.pathname);
    if (!analysisData && lastZip && onDetailRoute) {
      (async () => {
        try {
          const { data } = await axios.get(`${API}/zip-analysis/${lastZip}`);
          setAnalysisData(data);
        } catch (e) {
          // ignore; user can run a new analysis
        }
      })();
    }
  }, [location.pathname]);

  function validateZip(z) { return /^\d{5}(-\d{4})?$/.test(z.trim()); }

  function startProgressSimulation() { setOverallProgress(0); if (progressTimerRef.current) clearInterval(progressTimerRef.current); progressTimerRef.current = setInterval(() => { setOverallProgress((prev) => { if (prev >= 99) return prev; return Math.min(99, prev + 3); }); }, 800); }
  function stopProgressSimulation(finalValue = 100) { if (progressTimerRef.current) clearInterval(progressTimerRef.current); progressTimerRef.current = null; setOverallProgress(finalValue); }

  async function runAnalysis() {
    if (!validateZip(zip)) { setError("Please enter a valid ZIP code (e.g., 12345 or 12345-6789)"); return; }
    setLoading(true); setError(""); setSuccess(""); setAnalysisData(null);
    startProgressSimulation();
    navigate('/dashboard');
    try {
      await axios.post(`${API}/zip-analysis/start`, { zip_code: zip.trim() });
      let done = false;
      while (!done) {
        await new Promise(res => setTimeout(res, 2000));
        const { data: status } = await axios.get(`${API}/zip-analysis/status/${zip.trim()}`);
        setOverallProgress(status.overall_percent || 0);
        if (status.state === 'done') { done = true; break; }
        if (status.state === 'failed') { throw new Error(status.error || 'Analysis failed'); }
      }
      const response = await axios.get(`${API}/zip-analysis/${zip.trim()}`);
      setAnalysisData(response.data);
      localStorage.setItem('zipintel:last_zip', zip.trim());
      stopProgressSimulation(100);
      setSuccess("Analysis completed successfully!");
    } catch (err) {
      console.error("Analysis error:", err); stopProgressSimulation(overallProgress); setError(err.response?.data?.detail || err.message || "Failed to generate analysis. Please try again.");
    } finally { setLoading(false); }
  }

  function onSubmitZip(e) { e.preventDefault(); runAnalysis(); }

  const DetailLayout = ({ activeKey }) => (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100 flex">
      <IntelligenceSidebar
        analysisData={analysisData}
        activeCategory={activeKey}
        loading={loading}
        onNavigate={(type, title, obj) => {
          if (type === 'overview') navigate('/dashboard');
          else {
            const map = {
              buyer_migration: '/market-intelligence',
              seo_youtube_trends: '/seo-youtube-trends',
              content_strategy: '/content-strategy',
              content_assets: '/content-assets'
            };
            navigate(map[obj.key] || '/dashboard');
          }
        }}
        onBackToDashboard={() => navigate('/dashboard')}
      />
      <div className="flex-1 p-8">
        {loading ? (
          <Card>
            <CardContent>
              <div className="flex items-center gap-3">
                <Loader2 className="animate-spin" size={18} />
                <p className="text-sm text-neutral-600">Generating analysis...</p>
              </div>
            </CardContent>
          </Card>
        ) : !analysisData ? (
          <Card>
            <CardContent>
              <div className="text-center py-8">
                <MapPin className="mx-auto h-12 w-12 text-neutral-400 mb-4" />
                <h2 className="text-lg font-semibold text-neutral-900 mb-2">No Analysis Data</h2>
                <p className="text-sm text-neutral-600 mb-4">
                  You need to run an analysis first. Go back to the home page to enter a ZIP code.
                </p>
                <Button onClick={() => navigate('/')} variant="outline">
                  <ArrowLeft size={16} />
                  Back to Home
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : activeKey === 'buyer_migration' ? (
          <BuyerMigrationDetailView data={analysisData.buyer_migration} />
        ) : activeKey === 'seo_youtube_trends' ? (
          <SeoYouTubeDetail data={analysisData.seo_youtube_trends} />
        ) : activeKey === 'content_strategy' ? (
          <ContentStrategyDetail data={analysisData.content_strategy} />
        ) : activeKey === 'content_assets' ? (
          <ContentCreationDetail data={analysisData.content_assets} />
        ) : (
          <Card><CardContent><p className="text-sm text-neutral-600">Select a section from the sidebar.</p></CardContent></Card>
        )}
      </div>
    </div>
  );

  const HomePage = (
    <div className="mx-auto max-w-xl px-6 py-20">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-neutral-900 mb-4">ZIP Intel Generator</h1>
        <p className="text-lg text-neutral-600">Generate full intelligence (Buyer Migration, SEO/YouTube, Content Strategy, Assets) for any ZIP code</p>
      </div>
      <Card><CardContent>
        <form onSubmit={onSubmitZip} className="space-y-4">
          <div>
            <label htmlFor="zip" className="block text-sm font-medium text-neutral-700 mb-2">ZIP Code</label>
            <Input id="zip" value={zip} onChange={(e) => setZip(e.target.value)} placeholder="Enter ZIP code (e.g., 90210)" error={!!error} />
          </div>
          {error && (<Alert variant="error">{error}</Alert>)}
          <Button type="submit" disabled={loading || !zip.trim()} className="w-full">{loading ? (<><Loader2 className="animate-spin" size={18} />Analyzing...</>) : (<>Generate Intelligence</>)}</Button>
        </form>
      </CardContent></Card>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100">
      <Toast.Provider swipeDirection="right">
        {success && (<Toast.Root className="bg-green-50 border border-green-200 text-green-800 rounded-xl p-4 shadow-lg" open={!!success} onOpenChange={() => setSuccess("")}> <Toast.Title className="font-semibold">Success!</Toast.Title> <Toast.Description>{success}</Toast.Description> </Toast.Root>)}
        {error && (<Toast.Root className="bg-red-50 border border-red-200 text-red-800 rounded-xl p-4 shadow-lg" open={!!error} onOpenChange={() => setError("")}> <Toast.Title className="font-semibold">Error</Toast.Title> <Toast.Description>{error}</Toast.Description> </Toast.Root>)}
        <Toast.Viewport className="fixed bottom-0 right-0 p-6 w-96 z-50" />
      </Toast.Provider>

      <Routes>
        <Route path="/" element={HomePage} />
        <Route path="/dashboard" element={
          <IntelligenceDashboard
            analysisData={analysisData}
            loading={loading}
            overallProgress={overallProgress}
            taskProgress={taskProgress}
            onViewDetail={(key) => {
              const map = {
                buyer_migration: '/market-intelligence',
                seo_youtube_trends: '/seo-youtube-trends',
                content_strategy: '/content-strategy',
                content_assets: '/content-assets'
              };
              navigate(map[key] || '/dashboard');
            }}
          />
        } />
        <Route path="/market-intelligence" element={<DetailLayout activeKey="buyer_migration" />} />
        <Route path="/seo-youtube-trends" element={<DetailLayout activeKey="seo_youtube_trends" />} />
        <Route path="/content-strategy" element={<DetailLayout activeKey="content_strategy" />} />
        <Route path="/content-assets" element={<DetailLayout activeKey="content_assets" />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}