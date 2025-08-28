import React, { useState, useMemo } from "react";
import { 
  Loader2, 
  MapPin, 
  Sparkles, 
  Wand2, 
  FileText, 
  Mail, 
  Download, 
  ArrowLeft, 
  ExternalLink,
  AlertCircle,
  CheckCircle2
} from "lucide-react";
import * as Dialog from "@radix-ui/react-dialog";
import * as Tabs from "@radix-ui/react-tabs";
import * as Toast from "@radix-ui/react-toast";
import { Theme } from "@radix-ui/themes";
import BuyerMigrationDetail from "./components/BuyerMigrationDetail";
import JSZip from "jszip";
import { saveAs } from "file-saver";
import { jsPDF } from "jspdf";
import axios from "axios";
import "./App.css";
import "@radix-ui/themes/styles.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// UI Components using Radix
const Card = ({ className = "", children, ...props }) => (
  <div
    className={`rounded-2xl shadow-lg border border-neutral-200 bg-white ${className}`}
    {...props}
  >
    {children}
  </div>
);

const CardContent = ({ className = "", children }) => (
  <div className={`p-5 md:p-6 ${className}`}>{children}</div>
);

const Button = ({ className = "", variant = "default", children, disabled, ...props }) => {
  const baseClasses = "inline-flex items-center justify-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  const variants = {
    default: "bg-black text-white hover:bg-neutral-800 focus:ring-black disabled:bg-neutral-300",
    outline: "bg-white text-black border border-neutral-300 hover:bg-neutral-50 focus:ring-neutral-500",
    ghost: "bg-transparent text-neutral-700 hover:bg-neutral-100 focus:ring-neutral-500"
  };
  
  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

const Input = ({ className = "", error, ...props }) => (
  <input
    className={`w-full rounded-xl border px-4 py-3 text-base outline-none focus:ring-4 focus:ring-black/5 ${
      error ? 'border-red-300 focus:ring-red-100' : 'border-neutral-300'
    } ${className}`}
    {...props}
  />
);

const Alert = ({ variant = "default", children }) => {
  const variants = {
    default: "bg-blue-50 border-blue-200 text-blue-800",
    error: "bg-red-50 border-red-200 text-red-800",
    success: "bg-green-50 border-green-200 text-green-800"
  };
  
  return (
    <div className={`p-4 rounded-xl border ${variants[variant]} flex items-start gap-3`}>
      {variant === "error" && <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />}
      {variant === "success" && <CheckCircle2 className="w-5 h-5 mt-0.5 flex-shrink-0" />}
      <div className="text-sm">{children}</div>
    </div>
  );
};

export default function ZipIntelApp() {
  const [zip, setZip] = useState("");
  const [stage, setStage] = useState("home"); // home | pipeline | detail | asset
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [analysisData, setAnalysisData] = useState(null);
  const [detailView, setDetailView] = useState(null);
  const [assetDetail, setAssetDetail] = useState(null);

  const steps = useMemo(
    () => [
      { 
        id: "buyer_migration", 
        label: "Buyer Migration Intel", 
        icon: MapPin,
        key: "buyer_migration" 
      },
      { 
        id: "seo_youtube", 
        label: "SEO & YouTube Trends", 
        icon: Sparkles,
        key: "seo_youtube_trends" 
      },
      { 
        id: "content_strategy", 
        label: "Content Strategy", 
        icon: Wand2,
        key: "content_strategy" 
      },
      { 
        id: "hidden_listings", 
        label: "Hidden Listings (PDF)", 
        icon: FileText,
        key: "hidden_listings" 
      },
      { 
        id: "market_hooks", 
        label: "Market Hooks & Titles", 
        icon: Mail,
        key: "market_hooks" 
      },
      { 
        id: "content_assets", 
        label: "Content Assets", 
        icon: Download,
        key: "content_assets" 
      },
    ],
    []
  );

  function validateZip(z) {
    return /^\d{5}(-\d{4})?$/.test(z.trim());
  }

  async function runAnalysis() {
    if (!validateZip(zip)) {
      setError("Please enter a valid ZIP code (e.g., 12345 or 12345-6789)");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await axios.post(`${API}/zip-analysis`, {
        zip_code: zip.trim()
      });

      setAnalysisData(response.data);
      setStage("pipeline");
      setSuccess("Analysis completed successfully!");
      
    } catch (err) {
      console.error("Analysis error:", err);
      setError(err.response?.data?.detail || "Failed to generate analysis. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function downloadPDF() {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/generate-pdf/${zip}`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      saveAs(blob, `${zip}-hidden-listings.pdf`);
      setSuccess("PDF downloaded successfully!");
    } catch (err) {
      setError("Failed to download PDF");
    } finally {
      setLoading(false);
    }
  }

  async function downloadContentAsset(assetType, assetName) {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/content-asset/${zip}/${assetType}/${assetName}`);
      
      const blob = new Blob([response.data.content], { type: 'text/plain' });
      saveAs(blob, assetName);
      setSuccess("Content downloaded successfully!");
    } catch (err) {
      setError("Failed to download content");
    } finally {
      setLoading(false);
    }
  }

  function onSubmitZip(e) {
    e.preventDefault();
    runAnalysis();
  }

  function openDetail(stepKey, title) {
    if (!analysisData) return;
    
    const data = analysisData[stepKey];
    setDetailView({
      key: stepKey,
      title,
      data: data
    });
    setStage("detail");
  }

  function openAssetsDetail() {
    if (!analysisData?.content_assets) return;
    
    setDetailView({
      key: "content_assets",
      title: "Content Assets",
      data: analysisData.content_assets
    });
    setStage("detail");
  }

  return (
    <Theme>
      <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100">
      {/* Toast Notifications */}
      <Toast.Provider swipeDirection="right">
        {success && (
          <Toast.Root
            className="bg-green-50 border border-green-200 text-green-800 rounded-xl p-4 shadow-lg"
            open={!!success}
            onOpenChange={() => setSuccess("")}
          >
            <Toast.Title className="font-semibold">Success!</Toast.Title>
            <Toast.Description>{success}</Toast.Description>
          </Toast.Root>
        )}
        <Toast.Viewport className="fixed bottom-0 right-0 p-6 w-96 z-50" />
      </Toast.Provider>

      {/* Home Stage */}
      {stage === "home" && (
        <div className="mx-auto max-w-xl px-6 py-20">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-neutral-900 mb-4">
              ZIP Intel Generator
            </h1>
            <p className="text-lg text-neutral-600">
              Generate comprehensive real estate market intelligence for any ZIP code
            </p>
          </div>

          <Card>
            <CardContent>
              <form onSubmit={onSubmitZip} className="space-y-4">
                <div>
                  <label htmlFor="zip" className="block text-sm font-medium text-neutral-700 mb-2">
                    ZIP Code
                  </label>
                  <Input
                    id="zip"
                    value={zip}
                    onChange={(e) => setZip(e.target.value)}
                    placeholder="Enter ZIP code (e.g., 90210)"
                    error={!!error}
                  />
                </div>
                
                {error && (
                  <Alert variant="error">
                    {error}
                  </Alert>
                )}

                <Button 
                  type="submit" 
                  disabled={loading || !zip.trim()}
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <Loader2 className="animate-spin" size={18} />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} />
                      Generate Intelligence
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Pipeline Stage */}
      {stage === "pipeline" && analysisData && (
        <div className="mx-auto max-w-6xl px-6 py-10">
          <div className="mb-8">
            <Button
              variant="ghost"
              onClick={() => {
                setStage("home");
                setAnalysisData(null);
                setZip("");
              }}
              className="mb-4"
            >
              <ArrowLeft size={16} />
              New Analysis
            </Button>
            
            <h1 className="text-3xl font-bold text-neutral-900 mb-2">
              Market Intelligence for {zip}
            </h1>
            <p className="text-neutral-600">
              Generated on {new Date(analysisData.created_at).toLocaleDateString()}
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <ResultCard
              title="Buyer Migration Intel"
              value={analysisData.buyer_migration?.summary}
              onOpen={() => openDetail("buyer_migration", "Buyer Migration Intelligence")}
              icon={MapPin}
            />
            
            <ResultCard
              title="SEO & YouTube Trends"
              value={analysisData.seo_youtube_trends?.summary}
              onOpen={() => openDetail("seo_youtube_trends", "SEO & YouTube Trends")}
              icon={Sparkles}
            />
            
            <ResultCard
              title="Content Strategy"
              value={analysisData.content_strategy?.summary}
              onOpen={() => openDetail("content_strategy", "Content Strategy")}
              icon={Wand2}
            />
            
            <ResultCard
              title="Hidden Listings Analysis"
              value={analysisData.hidden_listings?.summary}
              onOpen={() => openDetail("hidden_listings", "Hidden Listings Analysis")}
              onDownload={downloadPDF}
              icon={FileText}
            />
            
            <ResultCard
              title="Market Hooks & Titles"
              value={analysisData.market_hooks?.summary}
              onOpen={() => openDetail("market_hooks", "Market Hooks & Titles")}
              icon={Mail}
            />
            
            <Card className="md:col-span-2">
              <CardContent>
                <div className="flex items-center gap-3 mb-3">
                  <Download className="w-5 h-5 text-neutral-600" />
                  <h3 className="font-semibold text-lg">Content Assets</h3>
                </div>
                <p className="text-neutral-600 mb-4">
                  {analysisData.content_assets?.summary}
                </p>
                <Button onClick={openAssetsDetail} variant="outline">
                  View All Assets
                  <ExternalLink size={14} />
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Detail Stage */}
      {stage === "detail" && detailView && (
        <div className="mx-auto max-w-4xl px-6 py-10">
          <Button
            variant="ghost"
            onClick={() => setStage("pipeline")}
            className="mb-6"
          >
            <ArrowLeft size={16} />
            Back to Overview
          </Button>

          <h1 className="text-2xl font-bold text-neutral-900 mb-6">
            {detailView.title}
          </h1>

          {detailView.key === "content_assets" ? (
            <ContentAssetsTabs 
              assets={detailView.data}
              onDownload={downloadContentAsset}
              onViewAsset={setAssetDetail}
              onSetStage={setStage}
            />
          ) : (
            <Card>
              <CardContent>
                <div className="prose prose-neutral max-w-none">
                  <pre className="whitespace-pre-wrap text-sm font-mono bg-neutral-50 p-6 rounded-xl">
                    {detailView.data?.detailed_analysis || "No detailed analysis available"}
                  </pre>
                </div>
                
                {detailView.key === "hidden_listings" && (
                  <div className="mt-6 pt-6 border-t">
                    <Button onClick={downloadPDF} disabled={loading}>
                      {loading ? (
                        <Loader2 className="animate-spin" size={16} />
                      ) : (
                        <Download size={16} />
                      )}
                      Download PDF Report
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Asset Detail Stage */}
      {stage === "asset" && assetDetail && (
        <div className="mx-auto max-w-4xl px-6 py-10">
          <Button
            variant="ghost"
            onClick={() => setStage("detail")}
            className="mb-6"
          >
            <ArrowLeft size={16} />
            Back to Assets
          </Button>

          <h1 className="text-2xl font-bold text-neutral-900 mb-6">
            {assetDetail.name}
          </h1>

          <Card>
            <CardContent>
              {assetDetail.type === "lead_magnet" ? (
                <div>
                  <Button
                    onClick={() => {
                      const blob = new Blob([assetDetail.content], { type: 'text/plain' });
                      saveAs(blob, `${assetDetail.name}.txt`);
                    }}
                    className="mb-6"
                  >
                    <Download size={16} />
                    Download Guide
                  </Button>
                  <div className="prose prose-neutral max-w-none">
                    <pre className="whitespace-pre-wrap text-sm bg-neutral-50 p-6 rounded-xl">
                      {assetDetail.content}
                    </pre>
                  </div>
                </div>
              ) : (
                <div>
                  <Button
                    onClick={() => downloadContentAsset(assetDetail.type, assetDetail.name)}
                    className="mb-6"
                    disabled={loading}
                  >
                    {loading ? (
                      <Loader2 className="animate-spin" size={16} />
                    ) : (
                      <Download size={16} />
                    )}
                    Download {assetDetail.type === "blog_posts" ? "Blog Post" : "Email"}
                  </Button>
                  <div className="prose prose-neutral max-w-none">
                    <pre className="whitespace-pre-wrap text-sm bg-neutral-50 p-6 rounded-xl">
                      {assetDetail.content}
                    </pre>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function ContentAssetsTabs({ assets, onDownload, onViewAsset, onSetStage }) {
  const [activeTab, setActiveTab] = useState("blogs");

  const tabData = [
    { id: "blogs", label: "Blog Posts", items: assets.blog_posts || [] },
    { id: "emails", label: "Email Campaigns", items: assets.email_campaigns || [] },
    { id: "lead_magnet", label: "Lead Magnet", items: [assets.lead_magnet] || [] }
  ];

  const currentItems = tabData.find(tab => tab.id === activeTab)?.items || [];

  return (
    <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
      <Tabs.List className="flex border-b border-neutral-200 mb-6">
        {tabData.map((tab) => (
          <Tabs.Trigger
            key={tab.id}
            value={tab.id}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? "border-black text-black"
                : "border-transparent text-neutral-500 hover:text-neutral-700"
            }`}
          >
            {tab.label}
          </Tabs.Trigger>
        ))}
      </Tabs.List>

      {tabData.map((tab) => (
        <Tabs.Content key={tab.id} value={tab.id}>
          <div className="space-y-4">
            {currentItems.map((item, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardContent className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-neutral-900">
                      {item?.name || `${tab.label} ${index + 1}`}
                    </h3>
                    <p className="text-sm text-neutral-600 mt-1">
                      {tab.id === "blogs" && "Blog post content"}
                      {tab.id === "emails" && "Email campaign content"}
                      {tab.id === "lead_magnet" && "Comprehensive buyer's guide"}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        onViewAsset({
                          ...item,
                          type: tab.id
                        });
                        onSetStage("asset");
                      }}
                    >
                      View
                      <ExternalLink size={14} />
                    </Button>
                    {tab.id !== "lead_magnet" && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onDownload(tab.id, item.name)}
                      >
                        <Download size={14} />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </Tabs.Content>
      ))}
    </Tabs.Root>
  );
}

function ResultCard({ title, value, onOpen, onDownload, icon: Icon }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent>
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            {Icon && <Icon className="w-5 h-5 text-neutral-600" />}
            <h3 className="font-semibold text-lg">{title}</h3>
          </div>
          <div className="flex gap-2">
            {onOpen && (
              <Button
                variant="outline"
                size="sm"
                onClick={onOpen}
              >
                View Details
                <ExternalLink size={14} />
              </Button>
            )}
            {onDownload && (
              <Button
                variant="outline"
                size="sm"
                onClick={onDownload}
              >
                <Download size={14} />
              </Button>
            )}
          </div>
        </div>
        <p className="text-neutral-600 text-sm">
          {value || "Generating..."}
        </p>
      </CardContent>
    </Card>
  );
}