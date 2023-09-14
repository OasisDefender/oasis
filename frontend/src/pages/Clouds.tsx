import React, { useState } from "react";

import {
    Alert,
    Button,
    Container,
    Group,
    LoadingOverlay,
    Modal,
    Space,
    Table,
    Text,
} from "@mantine/core";
import {
    IconAlertTriangle,
    IconCloudPlus,
    IconEye,
    IconRefresh,
} from "@tabler/icons-react";

import { ICloudCreate, ICloudView } from "../core/models/ICloud";
import { useClouds } from "../core/hooks/clouds";
import { CloudTableRow } from "../components/CloudTableRow";
import { useDisclosure } from "@mantine/hooks";
import { AddCloudForm } from "../components/AddCloudForm";
import { ShowModalError } from "../core/oasiserror";
import { AxiosError } from "axios";

export function Clouds() {    
    const {
        loading: cloudsLoading,
        error: cloudsError,
        clouds,
        fetchClouds,
        syncCloud,
        deleteCloud,
        addCloud,
    } = useClouds();

    const [
        addCloudModalOpened,
        { open: openAddCloudModal, close: closeAddCloudModal },
    ] = useDisclosure(false);
    const [infoShowed, { toggle: toggleInfoShowed }] = useDisclosure(false);
    const [addCloudInProgress, setAddCloudInProgress] = useState(false);
    const closeAddCloudModalIfNotInProgress = () => {
        if (!addCloudInProgress) {
            closeAddCloudModal();
        }
    };

    const onRefresh = () => {
        fetchClouds();
    };

    const makeSync = async (cloud: ICloudView) => {
        try {
            await syncCloud(cloud.id);
        } catch (e: unknown) {
            ShowModalError(
                `Cannot sync cloud "${cloud.name}"`,
                e as AxiosError
            );
        }
    };

    const makeDelete = async (cloud: ICloudView) => {
        try {
            await deleteCloud(cloud.id);
        } catch (e: unknown) {
            ShowModalError(
                `Cannot delete cloud "${cloud.name}"`,
                e as AxiosError
            );
        }
    };

    const makeAddCloud = async (cloud: ICloudCreate) => {
        setAddCloudInProgress(true);
        try {
            await addCloud(cloud);
            setAddCloudInProgress(false);
            closeAddCloudModal();
        } catch (e: unknown) {
            setAddCloudInProgress(false);
            ShowModalError(`Error while adding cloud`, e as AxiosError);
        }
    };

    const rows = clouds.map((cloud) => (
        <CloudTableRow
            key={cloud.id}
            cloud={cloud}
            makeSync={makeSync}
            makeDelete={makeDelete}
            infoShowed={infoShowed}
        />
    ));

    return (
        <>
            <Container>
                <Space h="sm" />
                <Group position="apart">
                    <Group>
                        <Button
                            leftIcon={<IconRefresh size="1.125rem" />}
                            loading={cloudsLoading}
                            onClick={onRefresh}
                        >
                            Refresh
                        </Button>
                        <Button
                            leftIcon={<IconCloudPlus size="1.125rem" />}
                            onClick={openAddCloudModal}
                        >
                            Add Cloud
                        </Button>
                    </Group>
                    <Group>
                        <Button
                            leftIcon={<IconEye size="1.125rem" />}
                            color="yellow"
                            onClick={toggleInfoShowed}
                        >
                            {infoShowed ? "Hide sensitive Info" : "Show sensitive info"}
                        </Button>
                    </Group>
                </Group>

                {!cloudsLoading && cloudsError == null && clouds.length > 0 && (
                    <Table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Cloud type</th>
                                <th>Additional information</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>{rows}</tbody>
                    </Table>
                )}

                {!cloudsLoading &&
                    cloudsError == null &&
                    clouds.length === 0 && (
                        <Text p={"xs"}>
                            You haven't added any clouds yet. Please add at
                            least one cloud.
                        </Text>
                    )}

                {!cloudsLoading && cloudsError != null && (
                    <Alert
                        icon={<IconAlertTriangle size="1rem" />}
                        title="Cannot get clouds"
                        color="red"
                        mt={"xs"}
                    >
                        {cloudsError}
                    </Alert>
                )}
            </Container>
            <Modal
                opened={addCloudModalOpened}
                onClose={closeAddCloudModalIfNotInProgress}
                title="Cloud access data"
                centered
            >
                <LoadingOverlay visible={addCloudInProgress} />
                <AddCloudForm
                    makeAddCloud={makeAddCloud}
                    onCancel={closeAddCloudModalIfNotInProgress}
                />
            </Modal>
        </>
    );
}
