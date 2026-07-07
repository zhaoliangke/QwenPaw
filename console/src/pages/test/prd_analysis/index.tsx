import { useState } from "react";
import {
  Card, Button, Table, Upload, Input, Space, message, Typography, Tag, Collapse,
} from "antd";
import {
  UploadOutlined, FileTextOutlined, PlayCircleOutlined,
  CheckCircleOutlined, WarningOutlined,
} from "@ant-design/icons";

const { TextArea } = Input;
const { Text, Paragraph } = Typography;

interface Story {
  id: string;
  title: string;
  as_a: string;
  i_want: string;
  so_that: string;
  priority: string;
  is_validated: boolean;
}

export default function PrdAnalysisPage() {
  const [parsedResult, setParsedResult] = useState<any>(null);
  const [stories, setStories] = useState<Story[]>([]);
  const [parsing, setParsing] = useState(false);
  const [generating, setGenerating] = useState(false);

  const handleUpload = async (file: File) => {
    setParsing(true);
    message.info(`正在解析 ${file.name}...`);
    const resp = await fetch("/api/test/prd/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_path: file.name, iteration_id: "current" }),
    });
    const data = await resp.json();
    setParsedResult(data);
    setParsing(false);
    message.success("解析完成");
    return false;
  };

  const handleGenerateStories = async () => {
    if (!parsedResult) return;
    setGenerating(true);
    const resp = await fetch("/api/test/prd/story/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ parsed_prd: parsedResult, iteration_id: "current" }),
    });
    const data = await resp.json();
    setStories(data.stories || []);
    setGenerating(false);
    message.success(`生成了 ${data.count || 0} 个 Story`);
  };

  const storyColumns = [
    { title: "标题", dataIndex: "title", key: "title" },
    {
      title: "格式", key: "format", width: 200,
      render: (_: unknown, r: Story) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          As a {r.as_a}, I want {r.i_want}, so that {r.so_that}
        </Text>
      ),
    },
    { title: "优先级", dataIndex: "priority", key: "priority", width: 80 },
    {
      title: "校验", key: "validated", width: 80,
      render: (_: unknown, r: Story) => r.is_validated
        ? <CheckCircleOutlined style={{ color: "green" }} />
        : <WarningOutlined style={{ color: "orange" }} />,
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Card title="需求分析" extra={<Button icon={<PlayCircleOutlined />} loading={parsing} type="primary">开始解析</Button>}>
        <Upload.Dragger beforeUpload={handleUpload} showUploadList={false} accept=".pdf,.docx,.doc,.md">
          <FileTextOutlined style={{ fontSize: 48, color: "#1677ff" }} />
          <Paragraph>点击或拖拽 PRD 文档到此区域 (PDF / Word / MD)</Paragraph>
        </Upload.Dragger>
      </Card>

      {parsedResult && (
        <Card title="解析结果" extra={
          <Button type="primary" loading={generating} onClick={handleGenerateStories}>
            生成 User Story
          </Button>
        }>
          <Collapse items={[
            { key: "flows", label: "业务流程", children: <Text>{(parsedResult.business_flows || ["待 AI 模型分析"]).join(", ") || "无"}</Text> },
            { key: "rules", label: "校验规则", children: <Text>{(parsedResult.validation_rules || ["待 AI 模型分析"]).join(", ") || "无"}</Text> },
            { key: "risks", label: "风险清单", children: parsedResult.risk_checklist?.length
              ? parsedResult.risk_checklist.map((r: string, i: number) => <Tag key={i} color="orange">{r}</Tag>)
              : <Text>无</Text>
            },
          ]} />
        </Card>
      )}

      {stories.length > 0 && (
        <Card title={`User Stories (${stories.length})`}>
          <Table dataSource={stories} columns={storyColumns} rowKey="id" pagination={false} />
        </Card>
      )}
    </Space>
  );
}
