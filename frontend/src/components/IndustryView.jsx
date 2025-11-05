import React, { useState, useEffect } from 'react'
import { Table, Card } from 'antd'
import { industryAPI } from '../services/api'

const IndustryView = () => {
  const [industries, setIndustries] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadIndustries()
  }, [])

  const loadIndustries = async () => {
    setLoading(true)
    try {
      const response = await industryAPI.getIndustries()
      if (response.code === 200) {
        setIndustries(response.data)
      }
    } catch (error) {
      console.error('加载行业数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    {
      title: '行业代码',
      dataIndex: 'code',
      key: 'code'
    },
    {
      title: '行业名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '涨跌幅',
      dataIndex: 'price_change',
      key: 'price_change',
      render: (val) => (
        <span style={{ color: val > 0 ? 'red' : 'green' }}>
          {val?.toFixed(2)}%
        </span>
      ),
      sorter: (a, b) => a.price_change - b.price_change
    },
    {
      title: '平均市盈率',
      dataIndex: 'pe_ratio',
      key: 'pe_ratio',
      render: (val) => val?.toFixed(2)
    },
    {
      title: '平均市净率',
      dataIndex: 'pb_ratio',
      key: 'pb_ratio',
      render: (val) => val?.toFixed(2)
    },
    {
      title: '股票数量',
      dataIndex: 'stock_count',
      key: 'stock_count'
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>行业分析</h1>

      <Card>
        <Table
          columns={columns}
          dataSource={industries}
          loading={loading}
          rowKey="code"
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </div>
  )
}

export default IndustryView
