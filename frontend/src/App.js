import React, { useState, useMemo, useEffect, useRef } from "react";
import { 
  Loader2, 
  MapPin, 
  Sparkles, 
  Wand2,
  ArrowLeft, 
  ExternalLink,
  AlertCircle,
  CheckCircle2,
  Mail
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
  const [availabilityResult, setAvailabilityResult] = useState(null); // New state for availability
  const [showAnalysisModal, setShowAnalysisModal] = useState(false); // Modal for ZIP analysis
  const [showPreviousZipsModal, setShowPreviousZipsModal] = useState(false); // Modal for previous ZIPs
  const [analysisZip, setAnalysisZip] = useState(""); // Separate ZIP for analysis modal
  const [analysisLoading, setAnalysisLoading] = useState(false); // Loading for analysis
  const [previousZips, setPreviousZips] = useState(() => {
    // Load previous ZIPs from localStorage
    const stored = localStorage.getItem('zipintel:previous_zips');
    return stored ? JSON.parse(stored) : [];
  });
  const progressTimerRef = useRef(null);

  useEffect(() => { setTaskProgress(computeTaskProgress(overallProgress)); }, [overallProgress]);

  // Attempt to hydrate analysis from last zip on deep links
  useEffect(() => {
    const lastZip = localStorage.getItem('zipintel:last_zip');
    const onDetailRoute = ["/dashboard","/market-intelligence","/seo-youtube-trends","/content-strategy","/content-assets"].includes(location.pathname);
    console.log('Hydration check:', { analysisData: !!analysisData, lastZip, onDetailRoute, pathname: location.pathname });
    
    if (!analysisData && lastZip && onDetailRoute) {
      console.log('Attempting to hydrate data for ZIP:', lastZip);
      console.log('API URL:', `${API}/zip-analysis/${lastZip}`);
      (async () => {
        try {
          const response = await axios.get(`${API}/zip-analysis/${lastZip}`);
          console.log('API Response Status:', response.status);
          console.log('API Response Data Keys:', Object.keys(response.data || {}));
          console.log('Successfully hydrated data for ZIP:', response.data?.zip_code);
          setAnalysisData(response.data);
        } catch (e) {
          console.error('Failed to hydrate data:', e.message);
          console.error('Error details:', e.response?.status, e.response?.statusText);
          // ignore; user can run a new analysis
        }
      })();
    } else if (!lastZip && onDetailRoute) {
      console.log('No lastZip found, setting a default for testing');
      // For testing purposes, set a default ZIP if we're on a detail route
      localStorage.setItem('zipintel:last_zip', '90210');
      // Force a re-run of this effect
      setTimeout(() => {
        window.location.reload();
      }, 100);
    }
  }, [location.pathname, analysisData]);

  function validateZip(z) { return /^\d{5}(-\d{4})?$/.test(z.trim()); }

  function startProgressSimulation() { setOverallProgress(0); if (progressTimerRef.current) clearInterval(progressTimerRef.current); progressTimerRef.current = setInterval(() => { setOverallProgress((prev) => { if (prev >= 99) return prev; return Math.min(99, prev + 3); }); }, 800); }
  function stopProgressSimulation(finalValue = 100) { if (progressTimerRef.current) clearInterval(progressTimerRef.current); progressTimerRef.current = null; setOverallProgress(finalValue); }

  async function runZipAnalysis() {
    if (!validateZip(analysisZip)) { 
      setError("Please enter a valid ZIP code (e.g., 12345 or 12345-6789)"); 
      return; 
    }
    
    setAnalysisLoading(true); 
    setError(""); 
    setSuccess(""); 
    setAnalysisData(null);
    startProgressSimulation();
    
    try {
      await axios.post(`${API}/zip-analysis/start`, { zip_code: analysisZip.trim() });
      let done = false;
      while (!done) {
        await new Promise(res => setTimeout(res, 2000));
        const { data: status } = await axios.get(`${API}/zip-analysis/status/${analysisZip.trim()}`);
        setOverallProgress(status.overall_percent || 0);
        if (status.state === 'done') { done = true; break; }
        if (status.state === 'failed') { throw new Error(status.error || 'Analysis failed'); }
      }
      const response = await axios.get(`${API}/zip-analysis/${analysisZip.trim()}`);
      setAnalysisData(response.data);
      localStorage.setItem('zipintel:last_zip', analysisZip.trim());
      
      // Add to previous ZIPs list
      const newPreviousZips = [...previousZips];
      const existingIndex = newPreviousZips.findIndex(z => z.zip === analysisZip.trim());
      if (existingIndex !== -1) {
        newPreviousZips.splice(existingIndex, 1); // Remove existing
      }
      newPreviousZips.unshift({
        zip: analysisZip.trim(),
        location: response.data.buyer_migration?.location || { city: 'Unknown', state: 'Unknown' },
        date: new Date().toLocaleDateString()
      });
      
      // Keep only last 10 ZIPs
      if (newPreviousZips.length > 10) {
        newPreviousZips.splice(10);
      }
      
      setPreviousZips(newPreviousZips);
      localStorage.setItem('zipintel:previous_zips', JSON.stringify(newPreviousZips));
      
      stopProgressSimulation(100);
      setSuccess("Analysis completed successfully!");
      setShowAnalysisModal(false);
      navigate('/dashboard');
    } catch (err) {
      console.error("Analysis error:", err); 
      stopProgressSimulation(overallProgress); 
      setError(err.response?.data?.detail || err.message || "Failed to generate analysis. Please try again.");
    } finally { 
      setAnalysisLoading(false); 
    }
  }

  function onSubmitAnalysis(e) { 
    e.preventDefault(); 
    runZipAnalysis(); 
  }

  function loadPreviousZip(zipData) {
    (async () => {
      try {
        const response = await axios.get(`${API}/zip-analysis/${zipData.zip}`);
        setAnalysisData(response.data);
        localStorage.setItem('zipintel:last_zip', zipData.zip);
        setShowPreviousZipsModal(false);
        navigate('/dashboard');
      } catch (e) {
        setError('Failed to load previous analysis');
      }
    })();
  }

  async function checkZipAvailability() {
    if (!validateZip(zip)) { 
      setError("Please enter a valid ZIP code (e.g., 12345 or 12345-6789)"); 
      return; 
    }
    
    setLoading(true); 
    setError(""); 
    setSuccess(""); 
    setAvailabilityResult(null);
    
    try {
      // For now, simulate availability check - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API delay
      
      // Mock availability logic - you'll replace this with actual API
      const isAvailable = Math.random() > 0.3; // 70% chance available for demo
      
      const result = {
        zipCode: zip.trim(),
        available: isAvailable,
        locationInfo: {
          city: isAvailable ? "Beverly Hills" : "Manhattan", // Mock data
          state: isAvailable ? "CA" : "NY",
          county: isAvailable ? "Los Angeles County" : "New York County"
        },
        pricing: isAvailable ? {
          monthlyFee: 299,
          setupFee: 99,
          annualDiscount: 0.15
        } : null,
        waitlistCount: isAvailable ? null : Math.floor(Math.random() * 50) + 10
      };
      
      setAvailabilityResult(result);
      
    } catch (err) {
      console.error("Availability check error:", err);
      setError("Failed to check availability. Please try again.");
    } finally { 
      setLoading(false); 
    }
  }

  function onSubmitZip(e) { 
    e.preventDefault(); 
    checkZipAvailability(); 
  }

  const ZipAnalysisModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-neutral-900">ZIP Code Analysis</h2>
          <button 
            onClick={() => setShowAnalysisModal(false)}
            className="text-neutral-400 hover:text-neutral-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form onSubmit={onSubmitAnalysis} className="space-y-6">
          <div>
            <label htmlFor="analysis-zip" className="block text-sm font-medium text-neutral-700 mb-2">
              Enter ZIP Code for Full Analysis
            </label>
            <Input 
              id="analysis-zip" 
              value={analysisZip} 
              onChange={(e) => setAnalysisZip(e.target.value)} 
              placeholder="Enter ZIP code (e.g., 90210)" 
              error={!!error}
            />
          </div>
          
          {error && (<Alert variant="error">{error}</Alert>)}
          
          <div className="flex gap-3">
            <Button 
              type="submit" 
              disabled={analysisLoading || !analysisZip.trim()} 
              className="flex-1"
            >
              {analysisLoading ? (
                <>
                  <Loader2 className="animate-spin" size={18} />
                  Generating...
                </>
              ) : (
                <>
                  <Wand2 className="w-4 h-4" />
                  Generate Analysis
                </>
              )}
            </Button>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => setShowAnalysisModal(false)}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );

  const PreviousZipsModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-neutral-900">Previous ZIP Codes</h2>
          <button 
            onClick={() => setShowPreviousZipsModal(false)}
            className="text-neutral-400 hover:text-neutral-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {previousZips.length === 0 ? (
          <div className="text-center py-8">
            <MapPin className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
            <p className="text-neutral-500">No previous ZIP codes analyzed yet.</p>
            <Button 
              className="mt-4" 
              onClick={() => {
                setShowPreviousZipsModal(false);
                setShowAnalysisModal(true);
              }}
            >
              <Wand2 className="w-4 h-4" />
              Run Your First Analysis
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-neutral-600 mb-4">
              Select a previously analyzed ZIP code to load its data:
            </p>
            
            {previousZips.map((zipData, index) => (
              <div 
                key={index}
                className="flex items-center justify-between p-3 border border-neutral-200 rounded-lg hover:bg-neutral-50 cursor-pointer"
                onClick={() => loadPreviousZip(zipData)}
              >
                <div>
                  <div className="font-semibold text-neutral-900">ZIP {zipData.zip}</div>
                  <div className="text-sm text-neutral-500">
                    {zipData.location.city}, {zipData.location.state}
                  </div>
                </div>
                <div className="text-xs text-neutral-400">
                  {zipData.date}
                </div>
              </div>
            ))}
            
            <Button 
              variant="outline" 
              className="w-full mt-4" 
              onClick={() => setShowPreviousZipsModal(false)}
            >
              Cancel
            </Button>
          </div>
        )}
      </div>
    </div>
  );

  const AvailableResult = ({ result }) => (
    <Card className="border-2 border-green-200 bg-green-50">
      <CardContent className="p-8 text-center">
        <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle2 className="w-8 h-8 text-white" />
        </div>
        
        <h2 className="text-2xl font-bold text-green-900 mb-2">
          🎉 ZIP {result.zipCode} is Available!
        </h2>
        <p className="text-green-700 text-lg mb-6">
          {result.locationInfo.city}, {result.locationInfo.state} • {result.locationInfo.county}
        </p>
        
        <div className="bg-white rounded-xl p-6 mb-6 border border-green-200">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Exclusive Territory Pricing</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-neutral-600">Monthly License Fee:</span>
              <span className="text-xl font-bold text-neutral-900">${result.pricing.monthlyFee}/mo</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-neutral-600">Setup Fee:</span>
              <span className="font-semibold text-neutral-900">${result.pricing.setupFee}</span>
            </div>
            <div className="border-t pt-3">
              <div className="flex justify-between items-center">
                <span className="text-green-600 font-medium">Annual Plan (Save 15%):</span>
                <span className="text-xl font-bold text-green-600">
                  ${Math.round(result.pricing.monthlyFee * 12 * (1 - result.pricing.annualDiscount))}/year
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="space-y-3">
          <Button className="w-full py-4 text-lg font-semibold bg-green-600 hover:bg-green-700">
            <Sparkles className="w-5 h-5" />
            Secure ZIP {result.zipCode} Now
          </Button>
          <Button variant="outline" className="w-full py-3" onClick={() => setAvailabilityResult(null)}>
            Check Another ZIP
          </Button>
        </div>
        
        <p className="text-xs text-neutral-500 mt-4">
          ⚡ Limited time: Reserve your territory with no commitment
        </p>
      </CardContent>
    </Card>
  );

  const UnavailableResult = ({ result }) => (
    <Card className="border-2 border-orange-200 bg-orange-50">
      <CardContent className="p-8 text-center">
        <div className="w-16 h-16 bg-orange-500 rounded-full flex items-center justify-center mx-auto mb-6">
          <AlertCircle className="w-8 h-8 text-white" />
        </div>
        
        <h2 className="text-2xl font-bold text-orange-900 mb-2">
          Sorry, ZIP {result.zipCode} is Taken
        </h2>
        <p className="text-orange-700 text-lg mb-6">
          {result.locationInfo.city}, {result.locationInfo.state} is already licensed to another agent
        </p>
        
        <div className="bg-white rounded-xl p-6 mb-6 border border-orange-200">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Join the Waitlist</h3>
          <p className="text-neutral-600 mb-4">
            Get notified if this territory becomes available. You'll be #{result.waitlistCount} in line.
          </p>
          
          <div className="space-y-3">
            <Input 
              placeholder="Enter your email address" 
              type="email"
              className="text-center"
            />
            <Button className="w-full bg-orange-600 hover:bg-orange-700">
              <Mail className="w-4 h-4" />
              Join Waitlist for ZIP {result.zipCode}
            </Button>
          </div>
        </div>
        
        <div className="space-y-3">
          <Button variant="outline" className="w-full py-3" onClick={() => setAvailabilityResult(null)}>
            <MapPin className="w-4 h-4" />
            Check Different ZIP Code
          </Button>
        </div>
        
        <p className="text-xs text-neutral-500 mt-4">
          💡 Tip: Try nearby ZIP codes - they might be available!
        </p>
      </CardContent>
    </Card>
  );

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
    <div className="mx-auto max-w-2xl px-6 py-20">
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
          <MapPin className="w-4 h-4" />
          Exclusive Territory Licensing
        </div>
        <h1 className="text-5xl font-bold text-neutral-900 mb-6">
          Secure Your <span className="text-blue-600">Exclusive</span> ZIP Code Territory
        </h1>
        <p className="text-xl text-neutral-600 leading-relaxed mb-2">
          Check if your desired ZIP code is available for exclusive real estate marketing rights
        </p>
        <p className="text-sm text-neutral-500">
          Only one agent per ZIP code. Once it's taken, it's gone.
        </p>
      </div>
      
      <Card className="shadow-xl border-2 border-neutral-100">
        <CardContent className="p-8">
          {!availabilityResult ? (
            <form onSubmit={onSubmitZip} className="space-y-6">
              <div>
                <label htmlFor="zip" className="block text-lg font-semibold text-neutral-900 mb-3">
                  Enter ZIP Code to Check Availability
                </label>
                <div className="relative">
                  <Input 
                    id="zip" 
                    value={zip} 
                    onChange={(e) => setZip(e.target.value)} 
                    placeholder="Enter ZIP code (e.g., 90210)" 
                    error={!!error}
                    className="text-lg py-4 pl-12 pr-4"
                  />
                  <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
                </div>
              </div>
              
              {error && (<Alert variant="error">{error}</Alert>)}
              
              <Button 
                type="submit" 
                disabled={loading || !zip.trim()} 
                className="w-full py-4 text-lg font-semibold"
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin" size={20} />
                    Checking Availability...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Check ZIP Availability
                  </>
                )}
              </Button>
            </form>
          ) : (
            <div>
              {availabilityResult.available ? (
                <AvailableResult result={availabilityResult} />
              ) : (
                <UnavailableResult result={availabilityResult} />
              )}
            </div>
          )}
          
          {!availabilityResult && (
            <div className="mt-8 pt-6 border-t border-neutral-200">
              <div className="flex items-center justify-center gap-8 text-sm text-neutral-600">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  Exclusive Rights
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  Market Intelligence
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  Lead Generation Tools
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
      
      <div className="text-center mt-8">
        <p className="text-sm text-neutral-500">
          Already have an account? <button 
            className="text-blue-600 hover:text-blue-700 font-medium"
            onClick={() => navigate('/dashboard')}
          >Sign in here</button>
        </p>
      </div>
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