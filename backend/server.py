@@
 @api_router.get("/content-asset/{zip_code}/{asset_type}/{asset_name}")
 async def get_content_asset(zip_code: str, asset_type: str, asset_name: str):
@@
     except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
+
+@api_router.post("/zip-analysis/assets/regenerate")
+async def regenerate_assets(request: ZipAnalysisRequest):
+    """Regenerate only content assets for an existing analysis."""
+    zip_code = request.zip_code
+    analysis = await db.market_intelligence.find_one({"zip_code": zip_code})
+    if not analysis:
+        raise HTTPException(status_code=404, detail="Analysis not found")
+    # Derive location from existing record
+    location_info = analysis.get('buyer_migration', {}).get('location') or {}
+    try:
+        svc = ZipIntelligenceService()
+        assets = await svc.generate_content_assets(zip_code, location_info)
+        await db.market_intelligence.update_one(
+            {"zip_code": zip_code},
+            {"$set": {"content_assets": assets, "updated_at": datetime.utcnow()}},
+        )
+        return assets
+    except Exception as e:
+        raise HTTPException(status_code=500, detail=f"Error regenerating assets: {str(e)}")
@@
 app.include_router(api_router)