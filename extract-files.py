#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    BlobFixupCtx,
    File,
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from extract_utils.tools import (
    llvm_objdump_path,
)
from extract_utils.utils import (
    run_cmd,
)

namespace_imports = [
    'hardware/oplus',
    'vendor/oneplus/sm8450-common',
    'hardware/qcom-caf/sm8450',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
]


def blob_fixup_nop_call(
    ctx: BlobFixupCtx,
    file: File,
    file_path: str,
    call_instruction: str,
    disassemble_symbol: str,
    symbol: str,
    *args,
    **kwargs,
):
    for line in run_cmd(
        [
            llvm_objdump_path,
            f'--disassemble-symbols={disassemble_symbol}',
            file_path,
        ]
    ).splitlines():
        line = line.split(maxsplit=3)

        if len(line) != 4:
            continue

        offset, _, instruction, args = line

        if instruction != call_instruction:
            continue

        if not args.endswith(f' <{symbol}>'):
            continue

        with open(file_path, 'rb+') as f:
            f.seek(int(offset[:-1], 16))
            f.write(b'\x1f\x20\x03\xd5')  # AArch64 NOP

        break


blob_fixups: blob_fixups_user_type = {
    'odm/bin/hw/vendor.oplus.hardware.biometrics.fingerprint@2.1-service': blob_fixup()
        .replace_needed('android.hardware.biometrics.common-V1-ndk_platform.so', 'android.hardware.biometrics.common-V1-ndk.so')
        .replace_needed('android.hardware.biometrics.fingerprint-V1-ndk_platform.so', 'android.hardware.biometrics.fingerprint-V1-ndk.so')
        .replace_needed('vendor.oplus.hardware.commondcs-V1-ndk_platform.so', 'vendor.oplus.hardware.commondcs-V1-ndk.so')
        .replace_needed('vendor.oplus.hardware.osense.client-V1-ndk_platform.so', 'vendor.oplus.hardware.osense.client-V1-ndk.so')
        .replace_needed('vendor.oplus.hardware.performance-V1-ndk_platform.so', 'vendor.oplus.hardware.performance-V1-ndk.so'),
    'odm/etc/camera/CameraHWConfiguration.config': blob_fixup()
        .regex_replace('SystemCamera =  0;  0;  1;  1;  1', 'SystemCamera =  0;  0;  0;  0;  1'),
    ('odm/lib64/libPerfectColor.so', 'odm/lib64/libCOppLceTonemapAPI.so', 'odm/lib64/libSuperRaw.so', 'odm/lib64/libYTCommon.so', 'odm/lib64/libaps_frame_registration.so', 'odm/lib64/libyuv2.so'): blob_fixup()
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
    ('odm/lib64/libAlgoProcess.so', 'vendor/lib64/libcamximageformatutils.so'): blob_fixup()
        .replace_needed('android.hardware.graphics.common-V2-ndk_platform.so', 'android.hardware.graphics.common-V6-ndk.so')
        .replace_needed('vendor.qti.hardware.display.config-V2-ndk_platform.so', 'vendor.qti.hardware.display.config-V5-ndk.so')
        .replace_needed('vendor.oplus.hardware.osense.client-V1-ndk_platform.so', 'vendor.oplus.hardware.osense.client-V1-ndk.so')
        .replace_needed('vendor.oplus.hardware.performance-V1-ndk_platform.so', 'vendor.oplus.hardware.performance-V1-ndk.so'),
    ('odm/lib64/libHIS.so', 'odm/lib64/libOGLManager.so'): blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    ('odm/lib64/libaiboost_hexagon.so', 'odm/lib64/libarcsoft_high_dynamic_range_v4.so'): blob_fixup()
        .clear_symbol_version('remote_handle_close')
        .clear_symbol_version('remote_handle_invoke')
        .clear_symbol_version('remote_handle_open')
        .clear_symbol_version('remote_handle64_close')
        .clear_symbol_version('remote_handle64_invoke')
        .clear_symbol_version('remote_handle64_open')
        .clear_symbol_version('remote_register_buf_attr')
        .clear_symbol_version('remote_register_buf'),
    ('odm/lib64/libarcsoft_dual_sat.so', 'odm/lib64/libarcsoft_dual_zoomtranslator.so', 'odm/lib64/libarcsoft_triple_sat.so', 'odm/lib64/libarcsoft_triple_zoomtranslator.so'): blob_fixup()
        .add_needed('libc++_shared.so'),
    'odm/lib64/libextensionlayer.so': blob_fixup()
        .replace_needed('libziparchive.so', 'libziparchive_odm.so'),
    'vendor/etc/libnfc-nci.conf': blob_fixup()
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    'vendor/etc/libnfc-nxp.conf': blob_fixup()
        .regex_replace('(NXPLOG_.*_LOGLEVEL)=0x03', '\\1=0x02')
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    'vendor/lib64/libmidasserviceintf_aidl.so': blob_fixup()
        .replace_needed('android.frameworks.stats-V1-ndk_platform.so', 'android.frameworks.stats-V1-ndk.so'),
    (
        'odm/lib64/vendor.oplus.hardware.cameraextension-V1-service-impl.so',
        'odm/lib64/libextensionlayer.so',
        'odm/lib64/camera/com.qti.sensor.imx615.so',
        'odm/lib64/camera/com.qti.sensor.imx789.so',
        'odm/lib64/camera/com.qti.sensor.ov08a10.so',
        'odm/lib64/camera/com.qti.sensor.s5kjn1sq03.so',
        'odm/lib64/vendor.oplus.hardware.sendextcamcmd-V1-service-impl.so',
        'vendor/lib64/com.qti.feature2.mfsr.so',
        'vendor/lib64/com.qti.feature2.rtmcx.so',
        'vendor/lib64/vendor.qti.hardware.camera.postproc@1.0-service-impl.so',
        'vendor/lib64/libcamxcommonutils.so',
        'vendor/lib64/com.qti.feature2.gs.sm8350.so',
        'vendor/lib64/com.qti.feature2.rt.so',
        'vendor/lib64/com.qualcomm.mcx.distortionmapper.so',
        'vendor/lib64/com.qti.feature2.fusion.so',
        'vendor/lib64/com.qti.feature2.rawhdr.so',
        'vendor/lib64/com.qti.feature2.mfsr.netrani.so',
        'vendor/lib64/com.qti.feature2.derivedoffline.so',
        'vendor/lib64/com.qti.feature2.mfsr.sm8450.so',
        'vendor/lib64/com.qualcomm.qti.mcx.usecase.extension.so',
        'vendor/lib64/com.qti.feature2.ml.so',
        'vendor/lib64/com.qti.feature2.memcpy.so',
        'vendor/lib64/com.qti.feature2.gs.sm8450.so',
        'vendor/lib64/com.qti.qseeutils.so',
        'vendor/lib64/com.qti.feature2.mcreprocrt.so',
        'vendor/lib64/com.qti.feature2.hdr.so',
        'vendor/lib64/com.qti.feature2.swmf.so',
        'vendor/lib64/com.qti.feature2.mux.so',
        'vendor/lib64/com.qti.feature2.ml.fillmore.so',
        'vendor/lib64/com.qti.feature2.gs.cedros.so',
        'vendor/lib64/com.qti.feature2.serializer.so',
        'vendor/lib64/com.qti.feature2.qcfa.so',
        'vendor/lib64/vendor.qti.hardware.camera.aon@1.0-service-impl.so',
        'vendor/lib64/com.qti.feature2.demux.so',
        'vendor/lib64/com.qti.feature2.mfsr.fillmore.so',
        'vendor/lib64/com.qti.feature2.statsregeneration.so',
        'vendor/lib64/com.qti.feature2.generic.so',
        'vendor/lib64/com.qualcomm.mcx.linearmapper.so',
        'vendor/lib64/hw/camera.qcom.so',
        'vendor/lib64/hw/com.qti.chi.override.so',
        'vendor/lib64/com.qti.chiusecaseselector.so',
        'vendor/lib64/libcamerapostproc.so',
        'vendor/lib64/com.qualcomm.mcx.policy.xr.so',
        'vendor/lib64/com.qti.feature2.frameselect.so',
        'vendor/lib64/com.qualcomm.mcx.policy.mfl.so',
        'vendor/lib64/com.qti.feature2.stub.so',
        'vendor/lib64/camera/components/com.qti.node.depth.so',
        'vendor/lib64/camera/components/com.qti.node.gme.so',
        'vendor/lib64/camera/components/com.bots.node.vendortagwrite.so',
        'vendor/lib64/camera/components/com.qti.node.ml.so',
        'vendor/lib64/camera/components/com.qti.node.hdr10pgen.so',
        'vendor/lib64/camera/components/com.qti.node.hdr10phist.so',
        'vendor/lib64/camera/components/libdepthmapwrapper_secure.so',
        'vendor/lib64/camera/components/com.qti.node.swregistration.so',
        'vendor/lib64/camera/components/com.qti.node.mlinference.so',
        'vendor/lib64/camera/components/com.qti.node.eisv2.so',
        'vendor/lib64/camera/components/com.qti.node.gyrornn.so',
        'vendor/lib64/camera/components/com.qti.node.dewarp.so',
        'vendor/lib64/camera/components/com.qti.camx.chiiqutils.so',
        'vendor/lib64/camera/components/com.qti.node.swec.so',
        'vendor/lib64/camera/components/com.qti.node.eisv3.so',
        'vendor/lib64/camera/components/com.arcsoft.node.eisv2.so',
        'vendor/lib64/com.qti.feature2.anchorsync.so',
        'vendor/lib64/com.qti.feature2.gs.fillmore.so',
        'vendor/lib64/com.qti.feature2.realtimeserializer.so',
        'vendor/lib64/com.qti.feature2.gs.sdm865.so',
    ): blob_fixup()
        .replace_needed('vendor.oplus.hardware.osense.client-V1-ndk_platform.so', 'vendor.oplus.hardware.osense.client-V1-ndk.so')
        .replace_needed('vendor.oplus.hardware.performance-V1-ndk_platform.so', 'vendor.oplus.hardware.performance-V1-ndk.so'),
    'odm/lib64/liboplus-uah-client.so': blob_fixup()
        .replace_needed('vendor.oplus.hardware.urcc-V1-ndk_platform.so', 'vendor.oplus.hardware.urcc-V1-ndk.so'),
}  # fmt: skip

module = ExtractUtilsModule(
    'wly',
    'oneplus',
    namespace_imports=namespace_imports,
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'sm8450-common', module.vendor
    )
    utils.run()
