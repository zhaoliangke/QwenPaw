import {useState} from "react";
import {
  Card, Button, Table, Space, message, Input,
} from "antd";
import {
  PlayCircleOutlined, BugOutlined, SaveOutlined,
  CodeOutlined,
} from "@ant-design/icons";

const { TextArea } = Input;

export default function UIAutoPage() {
  const [scripts, setScripts] = useState<any[]>([]);
  const [selectedScript, setSelectedScript] = useState<string>("");
  const [debugResult, setDebugResult] = useState<any>(null);
  const [debugging, setDebugging] = useState(false);

  const handleGenerate = async () => {
    const resp = await fetch("/api/test/ui-auto/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        test_case: { id: "tc-001", title: "登录功能", steps: ["打开登录页", "输入用户名", "输入密码", "点击登录"] },
        page_name: "LoginPage",
        iteration_id: "current",
      }),
    });
    const data = await resp.json();
    setScripts(prev => [...prev, data]);
    setSelectedScript(data.script_id);
    message.success("脚本生成成功");
  };

  const handleDebug = async () => {
    setDebugging(true);
    const resp = await fetch("/api/test/ui-auto/debug", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ script_content: selectedScript, test_case_id: selectedScript }),
    });
    const data = await resp.json();
    setDebugResult(data);
    setDebugging(false);
  };

  const columns = [
    { title: "脚本 ID", dataIndex: "script_id", key: "script_id", width: 200 },
    { title: "页面", dataIndex: "page", key: "page", width: 150 },
    { title: "步骤数", dataIndex: "steps_count", key: "steps_count", width: 80 },
    {
      title: "操作", key: "actions", width: 200,
      render: (_: unknown, _r: any) => (
        <Space size="small">
          <Button size="small" icon={<BugOutlined />} loading={debugging} onClick={handleDebug}>调试</Button>
          <Button size="small" icon={<PlayCircleOutlined />}>执行</Button>
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="UI 自动化脚本"
      extra={
        <Space>
          <Button type="primary" icon={<CodeOutlined />} onClick={handleGenerate}>生成脚本</Button>
          <Button icon={<SaveOutlined />}>保存</Button>
        </Space>
      }
    >
      <Space direction="vertical" size="middle" style={{ width: "100%" }}>
        <Table dataSource={scripts} columns={columns} rowKey="script_id" pagination={false} size="small" />
        {selectedScript && (
          <Card title="脚本编辑器" size="small">
            <TextArea rows={10} value={selectedScript} onChange={e => setSelectedScript(e.target.value)}
              style={{ fontFamily: "monospace", fontSize: 13 }} />
          </Card>
        )}
        {debugResult && (
          <Card title="调试结果" size="small">
            <pre style={{ fontSize: 12, maxHeight: 200, overflow: "auto" }}>
              {JSON.stringify(debugResult, null, 2)}
            </pre>
          </Card>
        )}
      </Space>
    </Card>
  );
}
