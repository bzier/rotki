﻿import { Message } from '@rotki/common/lib/messages';
import { computed, ref, unref } from '@vue/composition-api';
import { acceptHMRUpdate, defineStore } from 'pinia';
import Vue from 'vue';
import Vuex, { StoreOptions } from 'vuex';
import { api } from '@/services/rotkehlchen-api';
import { balances } from '@/store/balances';
import { defiSections, Section, Status } from '@/store/const';
import { storePlugins } from '@/store/debug';
import { defi } from '@/store/defi';
import { session } from '@/store/session';
import { settings } from '@/store/settings';
import { staking } from '@/store/staking';
import { statistics } from '@/store/statistics';
import { RotkehlchenState, StatusPayload, Version } from '@/store/types';
import { isLoading } from '@/store/utils';
import { Nullable } from '@/types';
import { LogLevel } from '@/utils/log-level';
import { getDefaultLogLevel, logger, setLevel } from '@/utils/logging';

Vue.use(Vuex);

let intervalId: any = null;

export const useMainStore = defineStore('main', () => {
  const newUser = ref(false);
  const message = ref(emptyMessage());
  const version = ref(defaultVersion());
  const connected = ref(false);
  const connectionFailure = ref(false);
  const status = ref<Partial<Record<Section, Status>>>({});
  const dataDirectory = ref('');
  const logLevel = ref<LogLevel>(getDefaultLogLevel());

  const updateNeeded = computed(() => {
    const { version: appVersion, downloadUrl } = version.value;
    return appVersion.indexOf('dev') >= 0 ? false : !!downloadUrl;
  });

  const detailsLoading = computed(() => {
    return (
      isLoading(unref(getStatus(Section.BLOCKCHAIN_ETH))) ||
      isLoading(unref(getStatus(Section.BLOCKCHAIN_BTC))) ||
      isLoading(unref(getStatus(Section.BLOCKCHAIN_KSM))) ||
      isLoading(unref(getStatus(Section.BLOCKCHAIN_AVAX))) ||
      isLoading(unref(getStatus(Section.EXCHANGES))) ||
      isLoading(unref(getStatus(Section.MANUAL_BALANCES)))
    );
  });

  const showMessage = computed(() => message.value.title.length > 0);

  const appVersion = computed(() => {
    const { version: appVersion } = version.value;
    const indexOfDev = appVersion.indexOf('dev');
    return indexOfDev > 0
      ? appVersion.substring(0, indexOfDev + 3)
      : appVersion;
  });

  const getVersion = async (): Promise<void> => {
    const { version: appVersion } = await api.info(true);
    if (appVersion) {
      version.value = {
        version: appVersion.ourVersion || '',
        latestVersion: appVersion.latestVersion || '',
        downloadUrl: appVersion.downloadUrl || ''
      };
    }
  };

  const getInfo = async (): Promise<void> => {
    const { dataDirectory: appDataDirectory, logLevel: level } = await api.info(
      false
    );
    dataDirectory.value = appDataDirectory;
    logLevel.value = level;
    setLevel(level);
  };

  const connect = async (payload?: string | null): Promise<void> => {
    let count = 0;
    if (intervalId) {
      clearInterval(intervalId);
    }

    function updateApi(payload?: Nullable<string>) {
      const interopBackendUrl = window.interop?.serverUrl();
      let backendUrl = api.defaultServerUrl;
      if (payload) {
        backendUrl = payload;
      } else if (interopBackendUrl) {
        backendUrl = interopBackendUrl;
      }
      api.setup(backendUrl);
    }

    const attemptConnect = async function () {
      try {
        updateApi(payload);

        const isConnected = !!(await api.ping());
        if (isConnected) {
          const accounts = await api.users();
          if (accounts.length === 0) {
            newUser.value = true;
          }
          clearInterval(intervalId);
          connected.value = isConnected;

          await getInfo();
          await getVersion();
        }
      } catch (e: any) {
        logger.error(e);
      } finally {
        count++;
        if (count > 20) {
          clearInterval(intervalId);
          connectionFailure.value = true;
        }
      }
    };
    intervalId = setInterval(attemptConnect, 2000);
    connectionFailure.value = false;
  };

  const setMessage = (msg: Message = emptyMessage()) => {
    message.value = msg;
  };

  const resetDefiStatus = () => {
    const newStatus = Status.NONE;
    defiSections.forEach(section => {
      status.value[section] = newStatus;
    });
  };

  const setStatus = ({ section, status: newStatus }: StatusPayload) => {
    const statuses = status.value;
    if (statuses[section] === newStatus) {
      return;
    }
    status.value = { ...statuses, [section]: newStatus };
  };

  const getStatus = (section: Section) =>
    computed<Status>(() => {
      return status.value[section] ?? Status.NONE;
    });

  const setConnected = (isConnected: boolean) => {
    connected.value = isConnected;
  };

  const setNewUser = (isNew: boolean) => {
    newUser.value = isNew;
  };

  const setConnectionFailure = (failed: boolean) => {
    connectionFailure.value = failed;
  };

  const reset = () => {
    newUser.value = false;
    message.value = emptyMessage();
    version.value = defaultVersion();
    connectionFailure.value = false;
    status.value = {};
  };

  return {
    newUser,
    message,
    version,
    appVersion,
    connected,
    connectionFailure,
    status,
    dataDirectory,
    updateNeeded,
    detailsLoading,
    showMessage,
    connect,
    getVersion,
    getInfo,
    setMessage,
    setStatus,
    getStatus,
    setConnected,
    setConnectionFailure,
    setNewUser,
    resetDefiStatus,
    reset
  };
});

const emptyMessage = (): Message => ({
  title: '',
  description: '',
  success: false
});

const defaultVersion = () =>
  ({
    version: '',
    latestVersion: '',
    downloadUrl: ''
  } as Version);

const store: StoreOptions<RotkehlchenState> = {
  modules: {
    balances,
    defi,
    session,
    settings,
    statistics,
    staking
  },
  plugins: storePlugins()
};
export default new Vuex.Store(store);

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMainStore, import.meta.hot));
}
