import { useState, useEffect, useCallback } from "react";
import {
  Card, Table, Button, Modal, Form, Input, DatePicker,
  Tag, Space, message, Popconfirm,
} from "antd";
import {
  PlusOutlined, ReloadOutlined, CameraOutlined,
  DiffOutlined, SyncOutlined,
} from "@ant-design/icons";

const { RangePicker } = DatePicker;

interface Iteration {
  id: string;
  name: string;
  version: string;
  module: string;
  start_date: string;
  end_date: string;
  status: string;
  git_branch?: string;
  test_environment?: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "default",
  reviewing: "processing",
  testing: "blue",
  released: "green",
  archived: "gray",
};

const STATUS_LABELS: Record<string, string> = {
  draft: "草稿",
  reviewing: "评审中",
  testing: "测试中",
  released: "已上线",
  archived: "已归档",
};

export default function IterationPage() {
  const [iterations, setIterations] = useState<Iteration[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const fetchIterations = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await fetch("/api/test/iteration/");
      const data = await resp.json();
      setIterations(Array.isArray(data) ? data : []);
    } catch {
      setIterations([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchIterations(); }, [fetchIterations]);

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      const body = {
        name: values.name,
        version: values.version,
        module: values.module,
        start_date: values.date_range[0].format("YYYY-MM-DD"),
        end_date: values.date_range[1].format("YYYY-MM-DD"),
        description: values.description || "",
        git_branch: values.git_branch || "",
        test_environment: values.test_environment || "",
      };
      const resp = await fetch("/api/test/iteration/", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (resp.ok) {
        message.success("迭代创建成功");
        setModalOpen(false);
        form.resetFields();
        fetchIterations();
      }
    } catch { /* validation error */ }
  };

  const handleSnapshot = async (id: string) => {
    await fetch(`/api/test/iteration/${id}/snapshot`, { method: "POST" });
    message.success("快照创建成功");
  };

  const columns = [
    { title: "名称", dataIndex: "name", key: "name", width: 200 },
    { title: "版本", dataIndex: "version", key: "version", width: 100 },
    { title: "模块", dataIndex: "module", key: "module", width: 150 },
    {
      title: "起止日期", key: "date", width: 220,
      render: (_: unknown, r: Iteration) => `${r.start_date} ~ ${r.end_date}`,
    },
    {
      title: "状态", dataIndex: "status", key: "status", width: 100,
      render: (s: string) => <Tag color={STATUS_COLORS[s] || "default"}>{STATUS_LABELS[s] || s}</Tag>,
    },
    {
      title: "操作", key: "actions", width: 280,
      render: (_: unknown, r: Iteration) => (
        <Space size="small">
          <Button size="small" icon={<CameraOutlined />} onClick={() => handleSnapshot(r.id)}>快照</Button>
          <Button size="small" icon={<DiffOutlined />}>对比</Button>
          <Popconfirm title="同步 Jira 需求?"><Button size="small" icon={<SyncOutlined />}>同步</Button></Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="迭代管理"
      extra={
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchIterations}>刷新</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>新建迭代</Button>
        </Space>
      }
    >
      <Table
        dataSource={iterations}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
      <Modal
        title="新建迭代"
        open={modalOpen}
        onOk={handleCreate}
        onCancel={() => { setModalOpen(false); form.resetFields(); }}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="迭代名称" rules={[{ required: true }]}>
            <Input placeholder="如: Sprint 1" />
          </Form.Item>
          <Form.Item name="version" label="版本号" rules={[{ required: true }]}>
            <Input placeholder="如: 2.1.0" />
          </Form.Item>
          <Form.Item name="module" label="模块" rules={[{ required: true }]}>
            <Input placeholder="如: 用户中心" />
          </Form.Item>
          <Form.Item name="date_range" label="起止日期" rules={[{ required: true }]}>
            <RangePicker style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="git_branch" label="关联 Git 分支">
            <Input placeholder="如: release/2.1.0" />
          </Form.Item>
          <Form.Item name="test_environment" label="测试环境">
            <Input placeholder="如: http://test.example.com" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
