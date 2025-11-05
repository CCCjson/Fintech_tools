import React, { useState, useEffect } from 'react'
import { Table, Input, Button, Space } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import { stockAPI } from '../services/api'

const StockList = () => {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  })

  useEffect(() => {
    loadStocks()
  }, [pagination.current])

  const loadStocks = async () => {
    setLoading(true)
    try {
      const response = await stockAPI.getStocks({
        page: pagination.current,
        per_page: pagination.pageSize
      })

      if (response.code === 200) {
        setStocks(response.data.items)
        setPagination({
          ...pagination,
          total: response.data.total
        })
      }
    } catch (error) {
      console.error('加载股票列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    {
      title: '股票代码',
      dataIndex: 'code',
      key: 'code'
    },
    {
      title: '股票名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '市场',
      dataIndex: 'market',
      key: 'market'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <a>详情</a>
          <a>分析</a>
        </Space>
      )
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>个股分析</h1>

      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索股票代码或名称"
          prefix={<SearchOutlined />}
          style={{ width: 300 }}
        />
        <Button type="primary">搜索</Button>
      </Space>

      <Table
        columns={columns}
        dataSource={stocks}
        loading={loading}
        rowKey="code"
        pagination={{
          ...pagination,
          onChange: (page) => setPagination({ ...pagination, current: page })
        }}
      />
    </div>
  )
}

export default StockList
