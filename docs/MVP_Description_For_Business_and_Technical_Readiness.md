Persistent UI elements include a navbar across the top for each of the four pillars and a chat panel along the right hand side where the GuideAgent (your trusted advisor throughout the journey) and a secondary chatbot (pillar specific liason to help you navigate within the given pillar)

Landing page welcomes you and introduces the key elements of your journey (the GuideAgent and Liaison agents plus the four pillars) and then the guide agent prompts the user to understand what brought them there today and how our MVP can help them.  based on the users goals it should suggest specific data that it would be helpful for them to share (e.g. volumetric data, operating procedures, financial reports, testing results, etc.) and then directs the user to the content pillar to continue their journey.

Content pillar is the first pillar in your journey.  it shows you a dashboard view of your available files, has a file uploader that supports multiple file types (including conditional logic for mainframe binary files and copybooks), and a parsing function that maps your file to an AI friendly format depending on the type of content (parquet, JSON Structured or JSON Chunks) and allows you to preview your data. Then it has a metadata extraction section for users who don't want our platform directly interacting with their data (or just want to see the metadata/schema details about their data) and also allows users to preview their metadata.  then it has a secondary chatbot (ContentLiaisonAgent) which allows you to interact with your parsed file and/or your content metadata. once your files are uploaded and parsed and the content metdata is extracted (if applicable). then you're ready to move onto the insights pillar.

Insights pillar starts with a file selection prompt (showing your parased files) and then section 2 has a formatted text element to provide business analysis of about your file and a secondary (side by side) element that provides either a visual or tabular representation of your data depending on your preferred learning style. the secondary chatbot (insight liaison) serves as a plain english guide to help you navigate your data and "double click on any initial analysis (e.g. I see I have a lot of customers who are more than 90 days late. can you show me who those customers are?) and uses the side-by-side elements in Section 2 to display the results. finally once you've gotten your answers/analysis there's a bottom section "insights summary" which recaps what you've learned on the page and supports it with an appropriate visual (chart or graph) and then provides recommendations based on the insights you've gained. now you're ready to move onto the operations pillar.

Operations Pillar:starts with 3 cards at the top allowing the user to either select an existing file(s) or upload a new file (redirects to the content pillar) or generate from scratch (triggers the Operations Liaison).  once you've selected your file(s) and clicked generate you move into section 2 where you'll see your file(s) translated into visual elements (workflow and SOP) and if only one is generated then you'll have a prompt to use AI to create the other. once you have both then it will activate the 3rd section "coexistence" where it will generate a coexistence blueprint that includes analysis and recommendations along with future state SOP and workflow artifacts. The custom development flow with the OperationsLiaison Agent allow the user to either describe their current process (works with workflowbuilderwizard to create the SOP element for section 2) or to get help designing their target state coexistence process (which would bypass section 2 and work with the coexistenceevaluator to create the coexistence blueprint).  once the coexistence blueprint is done then you're ready for the final step in the journey - the experience pillar.

Business Outcome Pillar: starts by displaying the summary outputs from the other pillars (what you uploaded in the Data Pillar; your Insights Summary from the Insights Pillar; and your Coexistence Blueprint from the Operations pillar). then the Experience Liaison (secondary chatbot) will prompt you for any additional context or files that you want to share before it prepares your final analysis which consists of a roadmap and a proposal for a POC project to get started.

---

## 🏗️ Architectural Foundation (Implementation Detail)

**Note for Technical Team:** All artifacts created during the MVP journey (workflows, SOPs, coexistence blueprints, roadmaps, POC proposals) are stored as platform artifacts (Solution/Journey artifacts) and can be discovered, versioned, and tracked via the platform's governance layer. This foundation enables future enhancements such as client collaboration (sharing artifacts for review and approval) and operational implementation (converting approved artifacts into executable solutions/journeys that run client operations on the platform).

**Key Implementation Points:**
- **Operations Pillar Artifacts:** Workflows, SOPs, and coexistence blueprints are stored as Journey artifacts via `JourneyOrchestratorService.create_journey_artifact()`
- **Business Outcomes Pillar Artifacts:** Roadmaps and POC proposals are stored as Solution artifacts via `SolutionComposerService.create_solution_artifact()`
- **Artifact Status:** All artifacts start in "draft" status and can transition through lifecycle (draft → review → approved → implemented → active)
- **Client Scoping:** Artifacts can be client-scoped (via `client_id` parameter) for multi-tenant support
- **Frontend Integration:** Artifacts include visualization data for frontend display, ensuring seamless user experience

**Future Enhancement Path:**
- Phase 1 (Weeks 1-2): Artifact storage foundation (complete)
- Phase 2 (Weeks 3-4): Client collaboration service (artifacts can be shared with clients for review)
- Phase 3 (Weeks 5-6): Implementation bridge (approved artifacts can be converted to operational solutions/journeys)
- Phase 4 (Weeks 7-8): MVP integration (all MVP orchestrators create artifacts)
- Phase 5 (Weeks 9-10): Client operations (clients can execute their approved solutions/journeys)

This architectural foundation ensures that MVP artifacts are not just display objects, but actual platform solutions/journeys that can evolve into operational infrastructure for client operations.
