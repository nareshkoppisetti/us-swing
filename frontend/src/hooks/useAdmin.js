'use client';
import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';

export function useSystemMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.getSystemMetrics()
      .then(d => setMetrics(d.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);
  return { metrics, loading };
}

export function useAdminAgentStatus() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.getAgentStatus()
      .then(d => setAgents(d.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);
  return { agents, loading };
}

export function useDataSources() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.getDataSources()
      .then(d => setSources(d.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);
  return { sources, loading };
}

export function useAdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const d = await api.getUsers();
      setUsers(d.data || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  const updateUser = useCallback(async (id, data) => {
    await api.updateUser(id, data);
    await fetch();
  }, [fetch]);

  const deleteUser = useCallback(async (id) => {
    await api.deleteUser(id);
    await fetch();
  }, [fetch]);

  const createUser = useCallback(async (data) => {
    await api.createUser(data);
    await fetch();
  }, [fetch]);

  return { users, loading, error, updateUser, deleteUser, createUser, refetch: fetch };
}

export function useAdminLogs(params = {}) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.getLogs(params)
      .then(d => setLogs(d.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [JSON.stringify(params)]);
  return { logs, loading };
}

export function useSystemConfig() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const d = await api.getSystemConfig();
      setConfig(d.data);
    } catch {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  const save = useCallback(async (data) => {
    setSaving(true);
    try {
      await api.updateSystemConfig(data);
      await fetch();
    } finally {
      setSaving(false);
    }
  }, [fetch]);

  return { config, loading, saving, save };
}
