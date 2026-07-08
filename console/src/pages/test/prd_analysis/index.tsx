import { useState, useCallback } from "react";
import {
  Card, Button, Table, Upload, Space, Typography, Collapse,
  Alert, Progress, Divider, Spin, Tabs,
} from "antd";
import {
  RocketOutlined,
  CloudUploadOutlined, LoadingOutlined,
} from "@ant-design/icons";

const { Text, Paragraph } = Typography;

interface ParseResult {
  status: string;
  file: string;
  iteration_id: string;
  business_flows: string[];
  validation_rules: string[];
  exception_flows: string[];
  risk_checklist: string[];
  functional_modules: string[];
  non_functional_requirements: string[];
  raw_text: string;
}

interface Story {
  id: string;
  title: string;
  as_a: string;
  i_want: string;
  so_that: string;
  priority: string;
}

interface TestCase {
  id: string;
  title: string;
  story_id: string;
  type: string;
  priority: string;
  steps: string[];
  expected: string;
}

type Phase = "idle" | "parsing" | "parsed" | "generating_stories" | "stories_done" | "generating_cases" | "done";

const SUCCESS_BG = "#f6ffed";
const SUCCESS_TEXT = "#389e0d";
const SUCCESS_BORDER = "#b7eb8f";
const WARN_BG = "#fffbe6";
const WARN_TEXT = "#d48806";
const WARN_BORDER = "#ffe58f";
const GRAY_BG = "#f5f5f5";
const GRAY_TEXT = "#666";
const GRAY_BORDER = "#d9d9d9";

function tagCss(color: string) {
  if (color === "green") return { bg: SUCCESS_BG, text: SUCCESS_TEXT, border: SUCCESS_BORDER };
  if (color === "yellow") return { bg: WARN_BG, text: WARN_TEXT, border: WARN_BORDER };
  return { bg: GRAY_BG, text: GRAY_TEXT, border: GRAY_BORDER };
}

const TAG_STYLE = { display: "inline-block", padding: "2px 10px", borderRadius: 4, fontSize: 12 };
const DOT_STYLE = { display: "inline-block", width: 6, height: 6, borderRadius: "50%", marginRight: 6 };

function renderTag(label: string, color: string) {
  const c = tagCss(color);
  const style = { ...TAG_STYLE, background: c.bg, color: c.text, border: "1px solid " + c.border };
  const dotStyle = { ...DOT_STYLE, background: c.text };
  return React.createElement("span", { style }, React.createElement("span", { style: dotStyle }), label);
}

export default function PrdAnalysisPage() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [fileName, setFileName] = useState("");
  const [parsedResult, setParsedResult] = useState<ParseResult | null>(null);
  const [stories, setStories] = useState<Story[]>([]);
  const [cases, setCases] = useState<TestCase[]>([]);
  const [activeTab, setActiveTab] = useState("result");

  const handleUpload = useCallback(async (file: File) => {
    setFileName(file.name);
    setPhase("parsing");
    setParsedResult(null);
    setStories([]);
    setCases([]);
    try {
      const content = await file.text();
      const resp = await fetch("/api/test/prd/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: file.name, iteration_id: "current", file_content: content }),
      });
      const data: ParseResult = await resp.json();
      setParsedResult(data);
      setPhase("parsed");
      if (data.raw_text) await generateStories(data);
    } catch { setPhase("idle"); }
    return false;
  }, []);

  const generateStories = async (parsed: ParseResult) => {
    setPhase("generating_stories");
    try {
      const resp = await fetch("/api/test/prd/story/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ parsed_prd: parsed, iteration_id: "current" }),
      });
      const data = await resp.json();
      setStories(data.stories || []);
      setPhase("stories_done");
    } catch { setPhase("parsed"); }
  };

  const generateTestCases = async () => {
    if (stories.length === 0) return;
    setPhase("generating_cases");
    const generated: TestCase[] = [];
    for (const story of stories.slice(0, 5)) {
      try {
        const resp = await fetch("/api/test/case/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ story, iteration_id: "current" }),
        });
        const data = await resp.json();
        if (data.cases) generated.push(...data.cases);
      } catch { /* skip */ }
    }
    setCases(generated);
    setPhase("done");
  };

  const isWorking = phase === "parsing" || phase === "generating_stories" || phase === "generating_cases";

  const getStoryColor = () => {
    if (stories.length > 0) return "green";
    if (phase === "generating_stories") return "yellow";
    return "gray";
  };

  const getCaseColor = () => {
    if (cases.length > 0) return "green";
    if (phase === "generating_cases") return "yellow";
    return "gray";
  };

  const storyColumns = [
    { title: "Title", dataIndex: "title", key: "title" },
    { title: "Story", key: "format", render: (_: unknown, r: Story) => <Text type="secondary" style={{ fontSize: 12 }}>As a {r.as_a}, I want {r.i_want}, so that {r.so_that}</Text> },
    { title: "Priority", dataIndex: "priority", key: "priority", width: 80, render: (v: string) => <span style={{ color: v === "high" ? "#ff4d4f" : v === "medium" ? "#faad14" : "#1677ff" }}>{v}</span> },
  ];

  const caseColumns = [
    { title: "Title", dataIndex: "title", key: "title" },
    { title: "Type", dataIndex: "type", key: "type", width: 100 },
    { title: "Priority", dataIndex: "priority", key: "priority", width: 80 },
    { title: "Expected", dataIndex: "expected", key: "expected" },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Card title="Upload PRD Document">
        <Upload.Dragger beforeUpload={handleUpload} showUploadList={false} accept=".pdf,.docx,.doc,.md,.txt" disabled={isWorking}>
          {isWorking ? <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} /> : <CloudUploadOutlined style={{ fontSize: 48, color: "#1677ff" }} />}
          <Paragraph style={{ marginTop: 16 }}>{isWorking ? "Processing..." : "Click or drag PRD document here"}</Paragraph>
        </Upload.Dragger>
        {phase !== "idle" && (
          <Progress percent={phase === "parsing" ? 30 : phase === "parsed" ? 50 : phase === "generating_stories" ? 70 : phase === "stories_done" ? 80 : phase === "generating_cases" ? 90 : 100} status={phase === "done" ? "success" : "active"} style={{ marginTop: 16 }} />
        )}
      </Card>

      {parsedResult && (
        <Card size="small">
          <Space split={<Divider type="vertical" />}>
            {renderTag("Parsed", "green")}
            {renderTag("Stories", getStoryColor())}
            {renderTag("Cases", getCaseColor())}
          </Space>
          {stories.length > 0 && cases.length === 0 && (
            <Button type="primary" icon={<RocketOutlined />} onClick={generateTestCases} loading={phase === "generating_cases"} style={{ marginTop: 12 }}>Generate Test Cases</Button>
          )}
        </Card>
      )}

      {parsedResult && (
        <Card title={"Result: " + fileName}>
          <Tabs activeKey={activeTab} onChange={setActiveTab} items={[
            { key: "result", label: "Analysis", children: <Collapse items={[
              { key: "flows", label: "Business Flows (" + (parsedResult.business_flows?.length || 0) + ")", children: (parsedResult.business_flows || []).length > 0 ? parsedResult.business_flows.map((f: string, i: number) => <span key={i} style={{ display: "inline-block", background: "#e6f7ff", color: "#0050b3", padding: "2px 8px", borderRadius: 4, margin: 4, fontSize: 12 }}>{f}</span>) : <Text type="secondary">None</Text> },
              { key: "modules", label: "Modules (" + (parsedResult.functional_modules?.length || 0) + ")", children: (parsedResult.functional_modules || []).length > 0 ? parsedResult.functional_modules.map((m: string, i: number) => <span key={i} style={{ display: "inline-block", background: "#f6ffed", color: "#237804", padding: "2px 8px", borderRadius: 4, margin: 4, fontSize: 12 }}>{m}</span>) : <Text type="secondary">None</Text> },
              { key: "rules", label: "Validation Rules (" + (parsedResult.validation_rules?.length || 0) + ")", children: (parsedResult.validation_rules || []).length > 0 ? parsedResult.validation_rules.map((r: string, i: number) => <span key={i} style={{ display: "inline-block", background: "#fff7e6", color: "#d48806", padding: "2px 8px", borderRadius: 4, margin: 4, fontSize: 12 }}>{r}</span>) : <Text type="secondary">None</Text> },
              { key: "risks", label: "Risks (" + (parsedResult.risk_checklist?.length || 0) + ")", children: (parsedResult.risk_checklist || []).length > 0 ? parsedResult.risk_checklist.map((r: string, i: number) => <span key={i} style={{ display: "inline-block", background: "#fff1f0", color: "#cf1322", padding: "2px 8px", borderRadius: 4, margin: 4, fontSize: 12 }}>{r}</span>) : <Text type="secondary">None</Text> },
            ]} /> },
            { key: "stories", label: "Stories (" + stories.length + ")", children: stories.length > 0 ? <Table dataSource={stories} columns={storyColumns} rowKey="id" pagination={false} /> : <Alert message="Will auto-generate" type="info" showIcon /> },
            { key: "cases", label: "Test Cases (" + cases.length + ")", children: cases.length > 0 ? <Table dataSource={cases} columns={caseColumns} rowKey="id" pagination={{ pageSize: 10 }} /> : <Alert message="Click Generate" type="info" showIcon /> },
          ]} />
        </Card>
      )}
    </Space>
  );
}
