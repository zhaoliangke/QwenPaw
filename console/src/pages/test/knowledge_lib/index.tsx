import {useState} from "react";
import {
  Card, Input, Button, Table, Space, message, Tag, Upload, Tree,
} from "antd";
import {
  SearchOutlined, UploadOutlined,
  ExperimentOutlined, ScheduleOutlined,
} from "@ant-design/icons";

const { Search } = Input;

export default function KnowledgeLibPage() {
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    setSearching(true);
    const resp = await fetch("/api/test/knowledge/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, limit: 10 }),
    });
    const data = await resp.json();
    setSearchResults(data.results || []);
    setSearching(false);
  };

  const handleArchive = async () => {
    const resp = await fetch("/api/test/knowledge/archive", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ iteration_id: "current" }),
    });
    const data = await resp.json();
    message.success(`归档完成: ${data.file_count || 0} 个文件`);
  };

  const treeData = [
    { title: "产品线 A", key: "pa", children: [
      { title: "模块 1", key: "pa-m1", children: [
        { title: "迭代 Sprint-1", key: "pa-m1-s1" },
      ]},
    ]},
    { title: "产品线 B", key: "pb" },
  ];

  const columns = [
    { title: "来源", dataIndex: "source", key: "source", width: 250 },
    {
      title: "类型", dataIndex: "type", key: "type", width: 100,
      render: (t: string) => <Tag color="blue">{t}</Tag>,
    },
    { title: "内容摘要", key: "content", ellipsis: true, render: (_: unknown, r: any) => r.content?.slice(0, 100) || "" },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Card title="知识库" extra={
        <Space>
          <Button icon={<ExperimentOutlined />} onClick={handleArchive}>归档当前迭代</Button>
          <Button icon={<ExperimentOutlined />}>AI 蒸馏</Button>
          <ScheduleOutlined />
        </Space>
      }>
        <Space direction="vertical" size="middle" style={{ width: "100%" }}>
          <Search
            placeholder="搜索历史需求、用例、缺陷..."
            enterButton={<><SearchOutlined /> 搜索</>}
            size="large"
            loading={searching}
            onSearch={handleSearch}
          />
          <div style={{ display: "flex", gap: 16 }}>
            <Card size="small" title="分类导航" style={{ width: 200 }}>
              <Tree treeData={treeData} defaultExpandAll />
            </Card>
            <Card size="small" title={<><UploadOutlined /> 上传文档</>} style={{ width: 200 }}>
              <Upload>
                <Button icon={<UploadOutlined />}>上传测试标准</Button>
              </Upload>
            </Card>
            <div style={{ flex: 1 }}>
              <Table dataSource={searchResults} columns={columns} rowKey="source"
                pagination={false} size="small" locale={{ emptyText: "输入搜索词查询知识库" }} />
            </div>
          </div>
        </Space>
      </Card>
    </Space>
  );
}
