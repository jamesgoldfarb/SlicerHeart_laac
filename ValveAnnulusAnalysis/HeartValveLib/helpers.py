""" collection of functions that are useful for several classes but non-specific to any """

import slicer
import logging


def getBinaryLabelmapRepresentation(segmentationNode, segmentID: str):
  segmentLabelmap = slicer.vtkOrientedImageData()
  segmentationNode.GetBinaryLabelmapRepresentation(segmentID, segmentLabelmap)
  return segmentLabelmap


def getSpecificHeartValveModelNodes(phases: list):
  heartValveModelNodes = []
  for phase in phases:
    try:
      heartValveModelNodes.extend(list(getValveModelNodesMatchingPhase(phase)))
    except ValueError as exc:
      logging.warning(exc)
  return heartValveModelNodes


def getSpecificHeartValveModelNodesMatchingPhaseAndType(phases: list, valveType: str, sort:bool=True):
  valveModels = []
  for valveModel in getAllHeartValveModelNodes():
    if valveModel.getValveType() == valveType and getValvePhaseShortName(valveModel) in phases:
      valveModels.append(valveModel)
  if sort:
    return sorted(valveModels, key=lambda valveModel: phases.index(getValvePhaseShortName(valveModel)))
  return valveModels


def getSpecificHeartValveMeasurementNodes(identifier):
  valveQuantificationLogic = slicer.modules.valvequantification.widgetRepresentation().self().logic
  validMeasurementNodes = []
  for measurementNode in getAllHeartValveMeasurementNodes():
    measurementPreset = valveQuantificationLogic.getMeasurementPresetByMeasurementNode(measurementNode)
    if not measurementPreset or measurementPreset.QUANTIFICATION_RESULTS_IDENTIFIER != identifier:
      continue
    validMeasurementNodes.append(measurementNode)
  return validMeasurementNodes


def getFirstValveModelNodeMatchingPhase(phase='MS'):
  for valveModelNode in getAllHeartValveModelNodes():
    if getValvePhaseShortName(valveModelNode) == phase:
      return valveModelNode
  raise ValueError("Could not find valve for phase %s" % phase)


def getFirstValveModelNodeMatchingSequenceIndex(seqIdx):
  for valveModelNode in getAllHeartValveModelNodes():
    if valveModelNode.getValveVolumeSequenceIndex() == seqIdx:
      return valveModelNode
  raise ValueError("Could not find valve for sequence index %s" % seqIdx)


def getValveModelNodesMatchingPhase(phase):
  for valveModelNode in getAllHeartValveModelNodes():
    if getValvePhaseShortName(valveModelNode) == phase:
      yield valveModelNode


def getFirstValveModelNodeMatchingPhaseAndType(phase, valveType):
  for valveModel in getValveModelNodesMatchingPhase(phase):
    if valveModel.getValveType() == valveType:
      return valveModel
  raise ValueError(f"Could not find valve with type {valveType} for phase {phase}")


def getValveModelNodesMatchingPhaseAndType(phase, valveType):
  valveModels = []
  for valveModel in getValveModelNodesMatchingPhase(phase):
    if valveModel.getValveType() == valveType:
      valveModels.append(valveModel)
  return valveModels


def getAllHeartValveModelNodes():
  import HeartValves
  return map(HeartValves.getValveModel, getAllHeartValveNodes())


def getAllHeartValveNodes():
  return getAllModuleSpecificScriptableNodes('HeartValve')


def getAllHeartValveMeasurementNodes():
  return getAllModuleSpecificScriptableNodes('HeartValveMeasurement')


def getAllModuleSpecificScriptableNodes(moduleName):
  return filter(lambda node: node.GetAttribute('ModuleName') == moduleName,
                slicer.util.getNodesByClass('vtkMRMLScriptedModuleNode'))


def getHeartValveMeasurementNode(phase):
  for measurementNode in getAllHeartValveMeasurementNodes():
    cardiacCyclePhaseNames = getMeasurementCardiacCyclePhaseShortNames(measurementNode)
    if len(cardiacCyclePhaseNames) == 1 and cardiacCyclePhaseNames[0] == phase:
      return measurementNode


def getMeasurementCardiacCyclePhaseShortNames(measurementNode):
  import ValveQuantification
  valveQuantificationLogic = ValveQuantification.ValveQuantificationLogic()
  return valveQuantificationLogic.getMeasurementCardiacCyclePhaseShortNames(measurementNode)


def getAllFilesWithExtension(directory, extension, file_name_only=False):
  import os
  import fnmatch
  files = []
  for root, dirnames, filenames in os.walk(directory):
    for filename in fnmatch.filter(filenames, '*{}'.format(extension)):
      files.append(filename if file_name_only else os.path.join(root, filename))
  return files


def isMRBFile(mrb_file):
  import os
  return os.path.isfile(mrb_file) and mrb_file.lower().endswith(".mrb")


def getValveModelForSegmentationNode(segmentationNode):
  for valveModel in getAllHeartValveModelNodes():
    if valveModel.getLeafletSegmentationNode() is segmentationNode:
      return valveModel
  return None


def getValvePhaseShortName(valveModel):
  cardiacPhase = valveModel.getCardiacCyclePhase()
  cardiacCyclePhasePreset = valveModel.cardiacCyclePhasePresets[cardiacPhase]
  return cardiacCyclePhasePreset['shortname']