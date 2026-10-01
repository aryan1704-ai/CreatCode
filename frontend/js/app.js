/* =========================================================
   CREATCODE — STAGE 24 (FIXED)
   Projects + History Integration
========================================================= */

const API_BASE_URL = "http://127.0.0.1:8000";

let currentLanguage = "Auto";
let currentExtension = "txt";

let selectedProjectId = null;
let projects = [];

const editor = document.getElementById("codeEditor");
const lineNumbers = document.getElementById("lineNumbers");
const languageBadge = document.getElementById("languageBadge");
const fileName = document.getElementById("fileName");
const cursorPosition = document.getElementById("cursorPosition");
const terminalOutput = document.getElementById("terminalOutput");

const promptInput = document.getElementById("promptInput");
const generateBtn = document.getElementById("generateBtn");

const projectSearch = document.getElementById("projectSearch");
const newProjectButton = document.querySelector(".new-project-button");

const analysisContent = document.getElementById("analysisContent");

const chatInput = document.getElementById("chatInput");
const chatSendBtn = document.getElementById("chatSendBtn");

const toastContainer = document.getElementById("toastContainer");


/* =========================================================
   SAMPLE CODE
========================================================= */

const sampleCode = `def find_largest(arr):
    if not arr:
        return None

    largest = arr[0]

    for num in arr:
        if num > largest:
            largest = num

    return largest


numbers = [34, 7, 23, 32, 5, 62, 14]

result = find_largest(numbers)
print(f"Largest number: {result}")`;

if (editor && !editor.value.trim()) {
    editor.value = sampleCode;
}


/* =========================================================
   HELPERS
========================================================= */

function capitalize(value) {
    if (!value) return "";
    return value.charAt(0).toUpperCase() + value.slice(1);
}

function escapeHTML(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function refreshIcons() {
    if (window.lucide) {
        lucide.createIcons();
    }

    // Icons are decorative: hide them from screen readers
    document.querySelectorAll("svg.lucide").forEach(icon => {
        icon.setAttribute("aria-hidden", "true");
        icon.setAttribute("focusable", "false");
    });
}


/* =========================================================
   TOAST
========================================================= */

function showToast(message, type = "info") {

    if (!toastContainer) {
        alert(message);
        return;
    }

    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(8px)";
        toast.style.transition = "0.2s ease";

        setTimeout(() => toast.remove(), 200);
    }, 2800);
}


/* =========================================================
   API REQUEST
========================================================= */

async function apiRequest(endpoint, options = {}) {

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const message =
            data?.message ||
            data?.detail ||
            `Request failed with status ${response.status}`;

        throw new Error(message);
    }

    // Backend may return rate-limit info with HTTP 200
    if (data && data.status === "rate_limited") {
        throw new Error(
            data.message || "Rate limit reached. Please try again later."
        );
    }

    return data;
}


/* =========================================================
   PROJECTS — LOAD
========================================================= */

async function loadProjects() {

    if (!projectsLoadedOnce) {
        renderProjectsSkeleton();
    }

    try {

        const data = await apiRequest("/api/projects/");

        if (Array.isArray(data)) {
            projects = data;
        } else if (Array.isArray(data?.projects)) {
            projects = data.projects;
        } else {
            projects = [];
        }

        projectsLoadedOnce = true;

        // Make sure the selected project still exists
        const exists = projects.some(
            project => Number(project.id) === Number(selectedProjectId)
        );

        if (!exists) {
            selectedProjectId = projects.length > 0 ? projects[0].id : null;
        }

        renderProjects(projects);
        updateProjectCount(projects.length);
        updateSelectedProjectUI();

        if (selectedProjectId) {
            loadProjectHistory(selectedProjectId);
        } else {
            renderHistory([]);
        }

    } catch (error) {

        console.error("Project loading error:", error);

        showToast(
            "Could not load projects. Check that the backend is running."
        );

        if (!projectsLoadedOnce) {
            renderProjectsError();
        }
    }
}


/* =========================================================
   PROJECTS — RENDER
========================================================= */

function renderProjects(projectList) {

    const recentSection = document.querySelector(".recent-section");

    if (!recentSection) return;

    const heading = recentSection.querySelector(".sidebar-heading");

    recentSection.innerHTML = "";

    if (heading) {
        recentSection.appendChild(heading);
    } else {
        const newHeading = document.createElement("div");
        newHeading.className = "sidebar-heading";
        newHeading.textContent = "RECENT PROJECTS";
        recentSection.appendChild(newHeading);
    }

    if (projectList.length === 0) {

        const empty = document.createElement("div");
        empty.style.padding = "12px 7px";
        empty.style.color = "#626979";
        empty.style.fontSize = "11px";
        empty.textContent = "No projects yet.";
        recentSection.appendChild(empty);

        return;
    }

    projectList.forEach(project => {

        const item = document.createElement("div");
        item.className = "recent-project";
        item.dataset.projectId = project.id;

        const language = detectProjectLanguage(project.name);

        const languageBox = document.createElement("div");
        languageBox.className = `project-language ${language.className}`;
        languageBox.textContent = language.label;

        const info = document.createElement("div");
        info.className = "recent-project-info";

        const name = document.createElement("div");
        name.className = "recent-project-name";
        name.textContent = project.name;

        const time = document.createElement("div");
        time.className = "recent-project-time";
        time.textContent = formatProjectDate(
            project.updated_at || project.created_at
        );

        info.appendChild(name);
        info.appendChild(time);

        item.appendChild(languageBox);
        item.appendChild(info);

        const deleteButton = document.createElement("button");
        deleteButton.className = "project-delete-button";
        deleteButton.type = "button";
        deleteButton.title = "Delete project";
        deleteButton.setAttribute(
            "aria-label",
            `Delete project ${project.name}`
        );
        deleteButton.innerHTML = `<i data-lucide="trash-2"></i>`;

        deleteButton.addEventListener("click", event => {
            event.stopPropagation();
            deleteProject(project.id);
        });

        // Row wrapper keeps the delete button OUTSIDE the clickable item
        // (a button nested inside a button is invalid for screen readers)
        const row = document.createElement("div");
        row.className = "recent-project-row";

        makeActivatable(item, () => selectProject(project.id));
        item.setAttribute("aria-label", `Open project ${project.name}`);

        row.appendChild(item);
        row.appendChild(deleteButton);
        recentSection.appendChild(row);
    });

    // Icons must be re-created every time the sidebar is rebuilt
    refreshIcons();
}


/* =========================================================
   PROJECT LANGUAGE
========================================================= */

function detectProjectLanguage(name = "") {

    const value = String(name).toLowerCase();

    if (
        value.includes("python") ||
        value.includes("django") ||
        value.includes("flask")
    ) {
        return { label: "Py", className: "python" };
    }

    if (
        value.includes("javascript") ||
        value.includes("js") ||
        value.includes("web")
    ) {
        return { label: "JS", className: "javascript" };
    }

    if (value.includes("java")) {
        return { label: "J", className: "java" };
    }

    return { label: "</>", className: "python" };
}


/* =========================================================
   PROJECT DATE
========================================================= */

function formatProjectDate(dateValue) {

    if (!dateValue) return "Recently";

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) return "Recently";

    const diff = new Date() - date;
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes} min ago`;

    const hours = Math.floor(minutes / 60);

    if (hours < 24) return `${hours} hr ago`;

    const days = Math.floor(hours / 24);

    if (days === 1) return "Yesterday";
    if (days < 7) return `${days} days ago`;

    return date.toLocaleDateString();
}


/* =========================================================
   PROJECT COUNT
========================================================= */

function updateProjectCount(total) {

    document.querySelectorAll(".sidebar-item").forEach(item => {

        if (item.textContent.includes("Projects")) {

            const countElement = item.querySelector(".sidebar-count");

            if (countElement) {
                countElement.textContent = total;
            }
        }
    });
}


/* =========================================================
   SELECT PROJECT
========================================================= */

function selectProject(projectId) {

    const project = projects.find(
        item => Number(item.id) === Number(projectId)
    );

    if (!project) return;

    selectedProjectId = project.id;

    updateSelectedProjectUI();

    showToast(`Project selected: ${project.name}`);

    loadProjectHistory(project.id);

    if (isMobileView()) showMobilePanel("code");
}


/* =========================================================
   SELECTED PROJECT UI
========================================================= */

function updateSelectedProjectUI() {

    document.querySelectorAll(".recent-project").forEach(item => {

        const id = Number(item.dataset.projectId);
        const isSelected = id === Number(selectedProjectId);

        item.classList.toggle("is-selected", isSelected);
        item.setAttribute("aria-current", isSelected ? "true" : "false");
    });
}


/* =========================================================
   CREATE PROJECT
========================================================= */

async function createProject() {

    const name = window.prompt("Enter project name:");

    if (!name || !name.trim()) return;

    const description = window.prompt(
        "Enter project description (optional):"
    );

    try {

        const project = await apiRequest("/api/projects/", {
            method: "POST",
            body: JSON.stringify({
                user_id: 1,
                name: name.trim(),
                description: description?.trim() || ""
            })
        });

        showToast(`Project "${project.name}" created successfully.`);

        if (project.id) {
            selectedProjectId = project.id;
        }

        await loadProjects();

    } catch (error) {

        console.error("Create project error:", error);

        showToast(error.message || "Could not create project.");
    }
}


/* =========================================================
   DELETE PROJECT
========================================================= */

async function deleteProject(projectId) {

    const project = projects.find(
        item => Number(item.id) === Number(projectId)
    );

    if (!project) return;

    const confirmed = window.confirm(`Delete project "${project.name}"?`);

    if (!confirmed) return;

    try {

        await apiRequest(`/api/projects/${projectId}`, {
            method: "DELETE"
        });

        projects = projects.filter(
            item => Number(item.id) !== Number(projectId)
        );

        if (Number(selectedProjectId) === Number(projectId)) {
            selectedProjectId = projects.length > 0 ? projects[0].id : null;
        }

        renderProjects(projects);
        updateProjectCount(projects.length);
        updateSelectedProjectUI();

        if (selectedProjectId) {
            loadProjectHistory(selectedProjectId);
        } else {
            renderHistory([]);
        }

        showToast(`Project "${project.name}" deleted.`);

    } catch (error) {

        console.error("Delete project error:", error);

        showToast(error.message || "Could not delete project.");
    }
}


/* =========================================================
   SEARCH PROJECTS
========================================================= */

function filterProjects() {

    const search = projectSearch?.value?.trim().toLowerCase() || "";

    if (!search) {
        renderProjects(projects);
        updateSelectedProjectUI();
        return;
    }

    const filtered = projects.filter(project => {

        const name = (project.name || "").toLowerCase();
        const description = (project.description || "").toLowerCase();

        return name.includes(search) || description.includes(search);
    });

    renderProjects(filtered);
    updateSelectedProjectUI();
}


/* =========================================================
   PROJECT HISTORY
========================================================= */

let historyItems = [];
let lastHistoryProjectId = null;

async function loadProjectHistory(projectId) {

    const list = document.getElementById("historyList");

    if (!list || !projectId) return;

    if (lastHistoryProjectId !== projectId) {
        renderHistorySkeleton();
    }

    lastHistoryProjectId = projectId;

    try {

        const data = await apiRequest(`/api/history/project/${projectId}`);

        historyItems = Array.isArray(data) ? data : (data?.history || []);

        renderHistory(historyItems);

    } catch (error) {

        console.error("History loading error:", error);

        lastHistoryProjectId = null;

        list.innerHTML =
            `<div class="history-empty">Could not load history.</div>`;
    }
}

function renderHistory(items) {

    const list = document.getElementById("historyList");

    if (!list) return;

    list.innerHTML = "";

    if (!items || items.length === 0) {
        list.innerHTML =
            `<div class="history-empty">No generations yet.</div>`;
        return;
    }

    items.forEach(entry => {

        const row = document.createElement("div");
        row.className = "history-item";

        row.innerHTML = `
            <div class="history-prompt">${escapeHTML(entry.prompt || "Untitled")}</div>
            <div class="history-time">${formatProjectDate(entry.created_at)}</div>
        `;

        makeActivatable(row, () => loadHistoryEntry(entry));

        list.appendChild(row);
    });
}

function loadHistoryEntry(entry) {

    const code = cleanGeneratedCode(
        entry.result || entry.generated_code || ""
    );

    if (!code || !editor) return;

    editor.value = code;
    updateEditorUI();

    if (promptInput) {
        promptInput.value = entry.prompt || "";
    }

    showToast("History entry loaded into editor.");

    if (isMobileView()) showMobilePanel("code");
}


/* =========================================================
   LANGUAGE DETECTION
========================================================= */

function detectLanguage(code) {

    const value = code || "";

    if (
        /<!DOCTYPE html>/i.test(value) ||
        /<html[\s>]/i.test(value) ||
        /<body[\s>]/i.test(value)
    ) {
        return "HTML";
    }

    if (
        /#include\s*[<"]/.test(value) ||
        /std::/.test(value) ||
        /cout\s*<</.test(value) ||
        /cin\s*>>/.test(value)
    ) {
        return "C++";
    }

    if (
        /public\s+static\s+void\s+main/.test(value) ||
        /System\.out\.println/.test(value) ||
        /ArrayList</.test(value)
    ) {
        return "Java";
    }

    if (
        /package\s+main/.test(value) ||
        /fmt\.Println/.test(value) ||
        /go\s+func/.test(value)
    ) {
        return "Go";
    }

    if (
        /fn\s+main\s*\(/.test(value) ||
        /let\s+mut\s+/.test(value) ||
        /println!\s*\(/.test(value)
    ) {
        return "Rust";
    }

    if (
        /\bdef\s+\w+\s*\(/.test(value) ||
        /\bfrom\s+\w+\s+import/.test(value) ||
        /^\s*import\s+\w+\s*$/m.test(value) ||
        /\bprint\s*\(/.test(value) ||
        /\belif\b/.test(value)
    ) {
        return "Python";
    }

    if (
        /console\.log\s*\(/.test(value) ||
        /\bconst\s+\w+/.test(value) ||
        /\blet\s+\w+/.test(value) ||
        /=>/.test(value)
    ) {
        return "JavaScript";
    }

    return "Auto";
}


/* =========================================================
   FILE EXTENSIONS
========================================================= */

function getExtension(language) {

    const extensions = {
        "Python": "py",
        "JavaScript": "js",
        "Java": "java",
        "C++": "cpp",
        "C": "c",
        "Go": "go",
        "Rust": "rs",
        "HTML": "html",
        "CSS": "css",
        "SQL": "sql",
        "PHP": "php"
    };

    return extensions[language] || "txt";
}


/* =========================================================
   UPDATE LANGUAGE UI
========================================================= */

function updateLanguage() {

    if (!editor) return;

    currentLanguage = detectLanguage(editor.value);
    currentExtension = getExtension(currentLanguage);

    if (languageBadge) {
        languageBadge.textContent =
            currentLanguage === "Auto"
                ? "Language: Auto"
                : `Language: Auto (${currentLanguage})`;
    }

    if (fileName) {
        fileName.textContent = `main.${currentExtension}`;
    }

    updateSyntaxHighlight();
}


/* =========================================================
   CLEAN GENERATED CODE
========================================================= */

function cleanGeneratedCode(text) {

    if (!text) return "";

    let result = text.trim();

    const fenced = result.match(
        /```(?:[a-zA-Z0-9+#.-]+)?\s*([\s\S]*?)```/
    );

    if (fenced) {
        result = fenced[1].trim();
    }

    result = result.replace(/^```[a-zA-Z0-9+#.-]*\s*/i, "");
    result = result.replace(/\s*```$/i, "");

    return result.trim();
}


/* =========================================================
   PRISM LANGUAGE + SYNTAX HIGHLIGHT
========================================================= */

function getPrismLanguage(language) {

    const map = {
        "Python": "python",
        "JavaScript": "javascript",
        "Java": "java",
        "C++": "cpp",
        "C": "c",
        "HTML": "markup",
        "CSS": "css",
        "SQL": "sql"
    };

    return map[language] || "none";
}

function updateSyntaxHighlight() {

    const highlight = document.getElementById("syntaxHighlight");

    if (!highlight || !editor) return;

    const language = getPrismLanguage(currentLanguage);

    if (
        window.Prism &&
        language !== "none" &&
        Prism.languages[language]
    ) {
        highlight.innerHTML = Prism.highlight(
            editor.value,
            Prism.languages[language],
            language
        );
    } else {
        highlight.textContent = editor.value;
    }

    highlight.scrollTop = editor.scrollTop;
    highlight.scrollLeft = editor.scrollLeft;
}


/* =========================================================
   LINE NUMBERS + CURSOR
========================================================= */

function updateLineNumbers() {

    if (!editor || !lineNumbers) return;

    const lineCount = editor.value.split("\n").length;

    lineNumbers.textContent = Array.from(
        { length: lineCount },
        (_, index) => index + 1
    ).join("\n");

    lineNumbers.scrollTop = editor.scrollTop;
}

function updateCursorPosition() {

    if (!editor || !cursorPosition) return;

    const beforeCursor = editor.value.substring(0, editor.selectionStart);
    const lines = beforeCursor.split("\n");

    const line = lines.length;
    const column = lines[lines.length - 1].length + 1;

    cursorPosition.textContent = `Ln ${line}, Col ${column}`;
}

function updateEditorUI() {
    updateLineNumbers();
    updateCursorPosition();
    updateLanguage();
}


/* =========================================================
   TERMINAL
========================================================= */

function appendTerminal(message, type = "") {

    if (!terminalOutput) return;

    const line = document.createElement("div");
    line.className = type ? `terminal-line ${type}` : "terminal-line";

    line.innerHTML = `
        <span class="terminal-prompt">$</span>
        <span>${escapeHTML(message)}</span>
    `;

    terminalOutput.appendChild(line);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}


/* =========================================================
   GENERATE CODE
========================================================= */

async function generateCode() {

    const prompt = promptInput?.value?.trim();

    if (!prompt) {
        showToast("Please describe what you want to build.");
        return;
    }

    if (!selectedProjectId) {
        showToast("Please create or select a project first.");
        return;
    }

    if (!generateBtn) return;

    const originalHTML = generateBtn.innerHTML;

    generateBtn.disabled = true;
    generateBtn.innerHTML = `<span>Generating...</span>`;

    appendTerminal("Generating code with CreatCode AI...");

    setEditorBusy(true);

    try {

        const data = await apiRequest("/api/generate/", {
            method: "POST",
            body: JSON.stringify({
                prompt: prompt,
                project_id: selectedProjectId
            })
        });

        const code = cleanGeneratedCode(data.result);

        if (editor) {
            editor.value = code;
            updateEditorUI();
        }

        appendTerminal("Code generated successfully.");
        showToast("Code generated successfully.");

        // Refresh projects because updated_at may have changed
        await loadProjects();

    } catch (error) {

        console.error("Generation error:", error);

        appendTerminal(`Generation failed: ${error.message}`);
        showToast(error.message || "Code generation failed.");

    } finally {

        setEditorBusy(false);

        generateBtn.disabled = false;
        generateBtn.innerHTML = originalHTML;

        refreshIcons();
    }
}


/* =========================================================
   AI ACTIONS
========================================================= */

async function convertCode() {

    if (!editor) return;

    const code = editor.value.trim();

    if (!code) {
        showToast("There is no code to convert.");
        return;
    }

    const defaultTarget =
        currentLanguage === "Python" ? "JavaScript" : "Python";

    const targetLanguage = window.prompt(
        "Convert to which language?",
        defaultTarget
    );

    if (!targetLanguage || !targetLanguage.trim()) return;

    const target = targetLanguage.trim();

    if (target.toLowerCase() === currentLanguage.toLowerCase()) {
        showToast(`The code is already ${currentLanguage}.`);
        return;
    }

    const button = document.querySelector('[data-action="convert"]');
    const originalHTML = button?.innerHTML;

    if (button) {
        button.disabled = true;
        button.innerHTML = "Converting...";
    }

    appendTerminal(`Converting code to ${target}...`);

    setEditorBusy(true);

    try {

        const data = await apiRequest("/api/convert/", {
            method: "POST",
            body: JSON.stringify({
                code: code,
                target_language: target
            })
        });

        if (data?.status !== "success") {
            throw new Error(data?.message || "Conversion failed.");
        }

        const convertedCode = cleanGeneratedCode(data.converted_code || "");

        if (!convertedCode) {
            throw new Error("Conversion returned empty code.");
        }

        editor.value = convertedCode;
        updateEditorUI();

        appendTerminal("Code converted successfully.", "terminal-success");
        showToast(`Code converted to ${target}.`);

    } catch (error) {

        console.error("Conversion error:", error);

        appendTerminal(
            `Conversion failed: ${error.message}`,
            "terminal-error"
        );

        showToast(error.message || "Could not convert code.");

    } finally {

        setEditorBusy(false);

        if (button) {
            button.disabled = false;
            button.innerHTML = originalHTML;
            refreshIcons();
        }
    }
}


async function runAIAction(action) {

    // Convert has its own flow (asks for a target language)
    if (action === "convert") {
        convertCode();
        return;
    }

    const code = editor?.value?.trim();

    if (!code) {
        showToast("There is no code to analyze.");
        return;
    }

    const endpointMap = {
        explain: "/api/explain/",
        debug: "/api/debug/",
        optimize: "/api/optimize/",
        testcases: "/api/testcases/",
        complexity: "/api/complexity/"
    };

    const endpoint = endpointMap[action];

    if (!endpoint) {
        showToast(`${action} integration is coming next.`);
        return;
    }

    const button = document.querySelector(`[data-action="${action}"]`);
    const originalHTML = button?.innerHTML;

    if (button) {
        button.disabled = true;
        button.innerHTML = "Working...";
    }

    try {

        showAnalysisSkeleton(action);

        const body =
            action === "debug"
                ? { code: code, error: "" }
                : { code: code };

        const data = await apiRequest(endpoint, {
            method: "POST",
            body: JSON.stringify(body)
        });

        let result = "";

        if (action === "explain") result = data.explanation || "";
        else if (action === "debug") result = data.debug_result || "";
        else if (action === "optimize") result = data.optimization || "";
        else if (action === "testcases") result = data.test_cases || "";
        else if (action === "complexity") result = data.analysis || "";

        displayAIResult(result, action);

        showToast(`${capitalize(action)} completed.`);

    } catch (error) {

        console.error(`${action} error:`, error);

        showAnalysisError(error.message || `${capitalize(action)} failed.`);

        showToast(error.message || `${capitalize(action)} failed.`);

    } finally {

        if (button) {
            button.disabled = false;
            button.innerHTML = originalHTML;
            refreshIcons();
        }
    }
}


/* =========================================================
   DISPLAY AI RESULT
========================================================= */

function displayAIResult(result, action) {

    if (!analysisContent) return;

    const title = `${capitalize(action)} Analysis`;

    const safeText = escapeHTML(String(result || ""));

    const formatted = safeText
        .replace(/^### (.*)$/gm, "<h3>$1</h3>")
        .replace(/^## (.*)$/gm, "<h2>$1</h2>")
        .replace(/^# (.*)$/gm, "<h1>$1</h1>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\n/g, "<br>");

    analysisContent.innerHTML = `
        <div class="analysis-result">
            <div class="assistant-label">CREATCODE AI</div>
            <h3>${title}</h3>
            <div class="analysis-result-body">${formatted}</div>
        </div>
    `;

    if (isMobileView()) showMobilePanel("analysis");
}


/* =========================================================
   RUN CODE (Stage 26B)
========================================================= */

async function runCode() {

    const code = editor?.value || "";

    if (!code.trim()) {
        showToast("There is no code to run.");
        return;
    }

    const runBtn = document.getElementById("runBtn");

    // Auto-detected languages the backend can't run fall back to a clear message
    const language =
        currentLanguage === "Auto" ? "Python" : currentLanguage;

    const originalHTML = runBtn?.innerHTML;

    if (runBtn) {
        runBtn.disabled = true;
        runBtn.innerHTML = "<span>Running...</span>";
    }

    appendTerminal(`Running ${language} code...`);

    setTerminalStatus("Running...", true);

    try {

        const data = await apiRequest("/api/run/", {
            method: "POST",
            body: JSON.stringify({
                code: code,
                language: language,
                stdin: ""
            })
        });

        if (data.output) {
            appendTerminal(data.output.trimEnd(), "terminal-output");
        }

        if (data.error) {
            appendTerminal(data.error.trimEnd(), "terminal-error");
        }

        if (data.status === "success") {

            const time = data.execution_time_ms ?? 0;

            appendTerminal(
                `Finished in ${time} ms (exit code ${data.exit_code}).`,
                "terminal-success"
            );

        } else {

            appendTerminal(
                data.message || "Execution failed.",
                "terminal-error"
            );
        }

    } catch (error) {

        console.error("Run error:", error);

        appendTerminal(`Run failed: ${error.message}`, "terminal-error");

        showToast(error.message || "Could not run the code.");

    } finally {

        setTerminalStatus("Ready");

        if (runBtn) {
            runBtn.disabled = false;
            runBtn.innerHTML = originalHTML;
            refreshIcons();
        }
    }
}


/* =========================================================
   COPY / DOWNLOAD
========================================================= */

async function copyCode() {

    if (!editor) return;

    const code = editor.value;

    if (!code.trim()) {
        showToast("There is no code to copy.");
        return;
    }

    try {
        await navigator.clipboard.writeText(code);
        showToast("Code copied to clipboard.");
    } catch {
        showToast("Could not copy code.");
    }
}

function downloadCode() {

    if (!editor) return;

    const code = editor.value;

    if (!code.trim()) {
        showToast("There is no code to download.");
        return;
    }

    const blob = new Blob([code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = `main.${currentExtension}`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(url);

    showToast("Code downloaded.");
}


/* =========================================================
   EDITOR KEYS + SCROLL
========================================================= */

function handleEditorKeydown(event) {

    if (!editor) return;

    // Ctrl + Enter = Generate
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        generateCode();
        return;
    }

    // Escape releases the Tab key so keyboard users can leave the editor
    if (event.key === "Escape") {
        editorTabReleased = true;
        return;
    }

    // Tab = four spaces (Shift+Tab, or Tab after Escape, moves focus)
    if (event.key === "Tab" && !event.shiftKey && !editorTabReleased) {

        event.preventDefault();

        const start = editor.selectionStart;
        const end = editor.selectionEnd;

        editor.value =
            editor.value.substring(0, start) +
            "    " +
            editor.value.substring(end);

        editor.selectionStart = editor.selectionEnd = start + 4;

        updateEditorUI();
    }
}

function syncEditorScroll() {

    const highlight = document.getElementById("syntaxHighlight");

    if (highlight) {
        highlight.scrollTop = editor.scrollTop;
        highlight.scrollLeft = editor.scrollLeft;
    }

    if (lineNumbers) {
        lineNumbers.scrollTop = editor.scrollTop;
    }
}


/* =========================================================
   SETUP: THEME
========================================================= */

function setupTheme() {

    const themeButton = document.getElementById("themeToggle");

    if (!themeButton) return;

    themeButton.addEventListener("click", () => {

        document.body.classList.toggle("light-mode");

        showToast(
            document.body.classList.contains("light-mode")
                ? "Light mode enabled."
                : "Dark mode enabled."
        );
    });
}


/* =========================================================
   SETUP: CHAT
========================================================= */

let chatHistory = [];
let chatBusy = false;
const MAX_CHAT_HISTORY = 10;


/* Turn an AI reply into safe HTML (code blocks, inline code, bold) */
function formatChatReply(text) {

    const parts = String(text || "").split("```");

    return parts.map((part, index) => {

        // Odd parts are fenced code blocks
        if (index % 2 === 1) {

            const code = part
                .replace(/^[a-zA-Z0-9+#.-]*\n/, "")
                .replace(/\n$/, "");

            return `
                <pre class="chat-code">
                    <div class="chat-code-actions">
                        <button type="button" class="chat-code-btn" data-chat-action="copy">Copy</button>
                        <button type="button" class="chat-code-btn" data-chat-action="insert">Use in editor</button>
                    </div>
                    <code>${escapeHTML(code)}</code>
                </pre>`;
        }

        return escapeHTML(part)
            .replace(/`([^`\n]+)`/g, "<code>$1</code>")
            .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>");

    }).join("");
}


function appendChatMessage(role, content, { html = false } = {}) {

    const messages = document.getElementById("chatMessages");

    if (!messages) return null;

    const item = document.createElement("div");
    item.className = role === "user" ? "chat-message" : "chat-message ai";

    const avatar = document.createElement("div");
    avatar.className = "chat-avatar";
    avatar.textContent = role === "user" ? "You" : "AI";

    const bubble = document.createElement("div");
    bubble.className = "chat-bubble";

    if (html) {
        bubble.innerHTML = content;
    } else {
        bubble.textContent = content;
    }

    item.appendChild(avatar);
    item.appendChild(bubble);
    messages.appendChild(item);

    messages.scrollTop = messages.scrollHeight;

    return item;
}


async function sendChatMessage() {

    if (chatBusy || !chatInput) return;

    const message = chatInput.value.trim();

    if (!message) return;

    chatBusy = true;

    if (chatSendBtn) chatSendBtn.disabled = true;

    chatInput.value = "";

    appendChatMessage("user", message);

    const thinking = appendChatMessage(
        "ai",
        `<span class="chat-typing"><span></span><span></span><span></span></span>`,
        { html: true }
    );

    try {

        const data = await apiRequest("/api/chat/", {
            method: "POST",
            body: JSON.stringify({
                message: message,
                code: editor?.value || "",
                language: currentLanguage,
                history: chatHistory.slice(-MAX_CHAT_HISTORY)
            })
        });

        const reply = data?.reply || "";

        if (!reply) {
            throw new Error("The AI returned an empty reply.");
        }

        thinking?.remove();

        appendChatMessage("ai", formatChatReply(reply), { html: true });

        chatHistory.push(
            { role: "user", content: message },
            { role: "assistant", content: reply }
        );

        chatHistory = chatHistory.slice(-MAX_CHAT_HISTORY);

    } catch (error) {

        console.error("Chat error:", error);

        thinking?.remove();

        appendChatMessage(
            "ai",
            `<span class="chat-error">${escapeHTML(error.message || "Chat failed.")}</span>`,
            { html: true }
        );

    } finally {

        chatBusy = false;

        if (chatSendBtn) chatSendBtn.disabled = false;

        chatInput.focus();
    }
}


function setupChat() {

    if (!chatSendBtn || !chatInput) return;

    chatSendBtn.addEventListener("click", sendChatMessage);

    // Enter sends, Shift+Enter adds a new line
    chatInput.addEventListener("keydown", event => {

        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendChatMessage();
        }
    });

    // Copy / "Use in editor" buttons inside AI code blocks
    const messages = document.getElementById("chatMessages");

    if (messages) {

        messages.addEventListener("click", async event => {

            const button = event.target.closest("[data-chat-action]");

            if (!button) return;

            const code =
                button.closest("pre")?.querySelector("code")?.textContent || "";

            if (!code) return;

            if (button.dataset.chatAction === "copy") {

                try {
                    await navigator.clipboard.writeText(code);
                    showToast("Code copied to clipboard.");
                } catch {
                    showToast("Could not copy code.");
                }

            } else if (button.dataset.chatAction === "insert" && editor) {

                editor.value = code;
                updateEditorUI();
                showToast("Code inserted into the editor.");

                if (isMobileView()) showMobilePanel("code");
            }
        });
    }
}


/* =========================================================
   SETUP: SEARCH
========================================================= */

function setupSearch() {

    if (!projectSearch) return;

    projectSearch.addEventListener("input", filterProjects);
}


/* =========================================================
   SETUP: PROJECTS   (this was the crashing function)
========================================================= */

function setupProjects() {

    if (newProjectButton) {
        newProjectButton.addEventListener("click", createProject);
    }

    // Projects sidebar navigation
    document.querySelectorAll(".sidebar-item").forEach(item => {

        item.addEventListener("click", () => {

            const text = item.textContent.trim();

            if (text.includes("Projects")) {
                focusSection(".recent-section");
            } else if (text.includes("History")) {
                focusSection(".history-section");
            }
        });
    });
}


/* =========================================================
   SETUP: AI ACTION BUTTONS
========================================================= */

function setupActions() {

    document.querySelectorAll(".action-button").forEach(button => {

        button.addEventListener("click", () => {

            const action = button.dataset.action;

            if (action) {
                runAIAction(action);
            }
        });
    });
}


/* =========================================================
   ACCESSIBILITY + KEYBOARD
========================================================= */

let editorTabReleased = false;

/* Make a non-button element behave like a button (Enter / Space) */
function makeActivatable(element, handler) {

    element.setAttribute("role", "button");
    element.tabIndex = 0;

    element.addEventListener("click", handler);

    element.addEventListener("keydown", event => {

        if (event.target !== element) return;

        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            handler(event);
        }
    });
}

function focusSection(selector) {

    const reduceMotion =
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    document.querySelector(selector)?.scrollIntoView({
        block: "start",
        behavior: reduceMotion ? "auto" : "smooth"
    });
}

function isTypingTarget(element) {

    return (
        !!element &&
        (/^(INPUT|TEXTAREA|SELECT)$/.test(element.tagName) ||
            element.isContentEditable)
    );
}


/* Inspector Analysis / Chat tabs with proper ARIA + arrow keys.
   (Replaces the inline <script> that used to live in index.html) */
function setupInspectorTabs() {

    const tabs = Array.from(document.querySelectorAll(".inspector-tab"));

    if (tabs.length === 0) return;

    const panels = {
        analysis: document.getElementById("analysisTab"),
        chat: document.getElementById("chatTab")
    };

    const tablist = document.querySelector(".inspector-tabs");

    tablist?.setAttribute("role", "tablist");
    tablist?.setAttribute("aria-label", "AI assistant sections");

    function select(tab, moveFocus = false) {

        tabs.forEach(item => {

            const active = item === tab;

            item.classList.toggle("active", active);
            item.setAttribute("aria-selected", String(active));
            item.tabIndex = active ? 0 : -1;
        });

        Object.entries(panels).forEach(([name, panel]) => {
            panel?.classList.toggle("active", name === tab.dataset.tab);
        });

        if (moveFocus) tab.focus();
    }

    tabs.forEach((tab, index) => {

        const name = tab.dataset.tab;

        tab.setAttribute("role", "tab");
        tab.id = `tab-${name}`;
        tab.setAttribute("aria-controls", `${name}Tab`);

        panels[name]?.setAttribute("role", "tabpanel");
        panels[name]?.setAttribute("aria-labelledby", tab.id);

        tab.addEventListener("click", () => select(tab));

        tab.addEventListener("keydown", event => {

            let target = null;

            if (event.key === "ArrowRight") {
                target = tabs[(index + 1) % tabs.length];
            } else if (event.key === "ArrowLeft") {
                target = tabs[(index - 1 + tabs.length) % tabs.length];
            } else if (event.key === "Home") {
                target = tabs[0];
            } else if (event.key === "End") {
                target = tabs[tabs.length - 1];
            }

            if (target) {
                event.preventDefault();
                select(target, true);
            }
        });
    });

    select(tabs.find(tab => tab.classList.contains("active")) || tabs[0]);
}


/* Labels, landmarks, live regions and keyboard shortcuts */
function setupAccessibility() {

    const setLabel = (selector, text) =>
        document.querySelector(selector)?.setAttribute("aria-label", text);

    // Landmarks
    setLabel(".sidebar", "Projects and history");
    setLabel(".inspector-panel", "AI assistant");

    const main = document.querySelector(".main-workspace");

    if (main) {
        main.id = "main";
        main.tabIndex = -1; // skip-link target
    }

    // Skip link (first thing a keyboard user tabs to)
    if (main && !document.querySelector(".skip-link")) {

        const skip = document.createElement("a");
        skip.className = "skip-link";
        skip.href = "#main";
        skip.textContent = "Skip to main content";

        skip.addEventListener("click", event => {
            event.preventDefault();
            if (isMobileView()) showMobilePanel("code");
            main.focus();
        });

        document.body.prepend(skip);
    }

    // Icon-only buttons
    setLabel("#themeToggle", "Toggle theme");
    setLabel('.icon-button[title="Settings"]', "Settings");
    setLabel("#copyBtn", "Copy code");
    setLabel("#downloadBtn", "Download code");
    setLabel(".inspector-settings", "Inspector settings");
    setLabel("#chatSendBtn", "Send message");
    setLabel("#closePromptModal", "Close dialog");

    // Form fields
    setLabel("#projectSearch", "Search projects");
    setLabel("#promptInput", "Describe what you want to build");
    setLabel("#chatInput", "Ask about your code");
    setLabel("#codeEditor", "Code editor");
    setLabel("#generatedPrompt", "Generated prompt");

    // Purely visual
    lineNumbers?.setAttribute("aria-hidden", "true");

    // Live regions (screen readers announce new content)
    terminalOutput?.setAttribute("role", "log");
    terminalOutput?.setAttribute("aria-live", "polite");
    terminalOutput?.setAttribute("aria-label", "Terminal output");

    const chatLog = document.getElementById("chatMessages");

    chatLog?.setAttribute("role", "log");
    chatLog?.setAttribute("aria-live", "polite");
    chatLog?.setAttribute("aria-label", "Chat messages");

    analysisContent?.setAttribute("aria-live", "polite");

    toastContainer?.setAttribute("role", "status");
    toastContainer?.setAttribute("aria-live", "polite");

    // Editor: explain the Tab behaviour to screen-reader users
    if (editor) {

        const hint = document.createElement("span");
        hint.id = "editorHint";
        hint.className = "sr-only";
        hint.textContent =
            "Press Tab to indent. Press Escape, then Tab, to leave the editor.";

        document.body.appendChild(hint);
        editor.setAttribute("aria-describedby", "editorHint");

        editor.addEventListener("blur", () => { editorTabReleased = false; });
        editor.addEventListener("input", () => { editorTabReleased = false; });
    }

    // Prompt box: Ctrl/Cmd + Enter generates (matches the on-screen hint)
    promptInput?.addEventListener("keydown", event => {

        if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
            event.preventDefault();
            generateCode();
        }
    });

    // Search: Escape clears and leaves the field
    projectSearch?.addEventListener("keydown", event => {

        if (event.key === "Escape") {
            projectSearch.value = "";
            filterProjects();
            projectSearch.blur();
        }
    });

    // Prompt modal semantics + Escape / backdrop to close
    const modal = document.getElementById("promptModal");

    if (modal) {

        modal.setAttribute("role", "dialog");
        modal.setAttribute("aria-modal", "true");

        const title = modal.querySelector("h2");

        if (title) {
            title.id = "promptModalTitle";
            modal.setAttribute("aria-labelledby", "promptModalTitle");
        }

        modal.addEventListener("click", event => {
            if (event.target === modal) modal.classList.remove("active");
        });

        document
            .getElementById("closePromptModal")
            ?.addEventListener("click", () => modal.classList.remove("active"));
    }

    // Global shortcuts
    document.addEventListener("keydown", event => {

        if (event.key === "Escape") {
            modal?.classList.remove("active");
        }

        // "/" focuses project search (the UI already shows this hint)
        if (
            event.key === "/" &&
            !event.ctrlKey && !event.metaKey && !event.altKey &&
            !isTypingTarget(document.activeElement)
        ) {
            event.preventDefault();

            if (isMobileView()) showMobilePanel("projects");

            projectSearch?.focus();
        }
    });
}


/* =========================================================
   LOADING STATES & SKELETONS
========================================================= */

let projectsLoadedOnce = false;

function renderProjectsSkeleton() {

    const section = document.querySelector(".recent-section");

    if (!section) return;

    const heading = section.querySelector(".sidebar-heading");

    section.innerHTML = "";

    if (heading) section.appendChild(heading);

    for (let i = 0; i < 4; i++) {

        const row = document.createElement("div");
        row.className = "skeleton-project";

        row.innerHTML = `
            <div class="skeleton skeleton-box"></div>
            <div class="skeleton-lines">
                <div class="skeleton skeleton-line"></div>
                <div class="skeleton skeleton-line shorter"></div>
            </div>
        `;

        section.appendChild(row);
    }
}

function renderProjectsError() {

    const section = document.querySelector(".recent-section");

    if (!section) return;

    const heading = section.querySelector(".sidebar-heading");

    section.innerHTML = "";

    if (heading) section.appendChild(heading);

    const box = document.createElement("div");
    box.className = "list-error";
    box.innerHTML = `
        <div>Could not load projects. Is the backend running?</div>
        <button type="button">Try again</button>
    `;

    box.querySelector("button").addEventListener("click", loadProjects);

    section.appendChild(box);
}

function renderHistorySkeleton() {

    const list = document.getElementById("historyList");

    if (!list) return;

    list.innerHTML = Array.from(
        { length: 3 },
        () => `<div class="skeleton skeleton-history"></div>`
    ).join("");
}

function showAnalysisSkeleton(action) {

    if (!analysisContent) return;

    analysisContent.innerHTML = `
        <div class="analysis-loading" role="status" aria-busy="true">
            <div class="analysis-loading-label">
                <span class="btn-spinner"></span>
                ${escapeHTML(capitalize(action))} in progress...
            </div>
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-line"></div>
            <div class="skeleton skeleton-line"></div>
            <div class="skeleton skeleton-line short"></div>
            <div class="skeleton skeleton-block"></div>
            <div class="skeleton skeleton-line"></div>
            <div class="skeleton skeleton-line shorter"></div>
        </div>
    `;
}

function showAnalysisError(message) {

    if (!analysisContent) return;

    analysisContent.innerHTML = `
        <div class="analysis-error">
            <i data-lucide="triangle-alert"></i>
            <h3>Something went wrong</h3>
            <p>${escapeHTML(message || "Please try again.")}</p>
        </div>
    `;

    refreshIcons();
}

function setEditorBusy(isBusy) {

    document
        .querySelector(".code-editor-wrapper")
        ?.classList.toggle("is-generating", isBusy);

    // Stop typing while AI is about to replace the content
    if (editor) editor.readOnly = isBusy;
}

function setTerminalStatus(text, busy = false) {

    const status = document.querySelector(".terminal-status");

    if (!status) return;

    status.textContent = text;
    status.classList.toggle("is-busy", busy);
}


/* =========================================================
   MOBILE NAVIGATION (one panel at a time on phones)
========================================================= */

const mobileQuery = window.matchMedia("(max-width: 900px)");

function isMobileView() {
    return mobileQuery.matches;
}

/* panel = "projects" | "code" | "analysis" | "chat" */
function showMobilePanel(panel) {

    const layout = document.querySelector(".workspace-layout");

    if (!layout) return;

    layout.dataset.mobilePanel = panel;

    document.querySelectorAll(".mobile-nav-item").forEach(button => {

        const active = button.dataset.panel === panel;

        button.classList.toggle("active", active);
        button.setAttribute("aria-current", active ? "page" : "false");
    });

    // Reuse the existing Analysis / Chat tab switching
    if (panel === "analysis" || panel === "chat") {
        document
            .querySelector(`.inspector-tab[data-tab="${panel}"]`)
            ?.click();
    }
}

function setupMobileNav() {

    document.querySelectorAll(".mobile-nav-item").forEach(button => {
        button.addEventListener("click", () => {
            showMobilePanel(button.dataset.panel);
        });
    });

    showMobilePanel("code");
}


/* =========================================================
   INITIALIZE
========================================================= */

async function initializeApp() {

    // Editor
    if (editor) {
        editor.addEventListener("input", updateEditorUI);
        editor.addEventListener("click", updateCursorPosition);
        editor.addEventListener("keyup", updateCursorPosition);
        editor.addEventListener("keydown", handleEditorKeydown);
        editor.addEventListener("scroll", syncEditorScroll);
    }

    // Generate
    if (generateBtn) {
        generateBtn.addEventListener("click", generateCode);
    }

    // Run
    const runBtn = document.getElementById("runBtn");

    if (runBtn) {
        runBtn.addEventListener("click", runCode);
    }

    // Copy
    const copyBtn = document.getElementById("copyBtn");

    if (copyBtn) {
        copyBtn.addEventListener("click", copyCode);
    }

    // Download
    const downloadBtn = document.getElementById("downloadBtn");

    if (downloadBtn) {
        downloadBtn.addEventListener("click", downloadCode);
    }

    setupActions();
    setupProjects();
    setupSearch();
    setupTheme();
    setupChat();
    setupMobileNav();
    setupInspectorTabs();
    setupAccessibility();

    // Initial editor state
    updateEditorUI();

    // Load projects from MySQL
    await loadProjects();

    refreshIcons();
}


/* =========================================================
   START APPLICATION
========================================================= */

document.addEventListener("DOMContentLoaded", initializeApp);