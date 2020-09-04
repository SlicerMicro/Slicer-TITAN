/*==============================================================================

  Program: 3D Slicer

  Portions (c) Copyright Brigham and Women's Hospital (BWH) All Rights Reserved.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

==============================================================================*/

// HyperionModuleCode Logic includes
#include <vtkSlicerHyperionModuleCodeLogic.h>

// HyperionModuleCode includes
#include "qSlicerHyperionModuleCodeModule.h"
#include "qSlicerHyperionModuleCodeModuleWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerHyperionModuleCodeModulePrivate
{
public:
  qSlicerHyperionModuleCodeModulePrivate();
};

//-----------------------------------------------------------------------------
// qSlicerHyperionModuleCodeModulePrivate methods

//-----------------------------------------------------------------------------
qSlicerHyperionModuleCodeModulePrivate::qSlicerHyperionModuleCodeModulePrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerHyperionModuleCodeModule methods

//-----------------------------------------------------------------------------
qSlicerHyperionModuleCodeModule::qSlicerHyperionModuleCodeModule(QObject* _parent)
  : Superclass(_parent)
  , d_ptr(new qSlicerHyperionModuleCodeModulePrivate)
{
}

//-----------------------------------------------------------------------------
qSlicerHyperionModuleCodeModule::~qSlicerHyperionModuleCodeModule()
{
}

//-----------------------------------------------------------------------------
QString qSlicerHyperionModuleCodeModule::helpText() const
{
  return "This is a loadable module that can be bundled in an extension";
}

//-----------------------------------------------------------------------------
QString qSlicerHyperionModuleCodeModule::acknowledgementText() const
{
  return "This work was partially funded by NIH grant NXNNXXNNNNNN-NNXN";
}

//-----------------------------------------------------------------------------
QStringList qSlicerHyperionModuleCodeModule::contributors() const
{
  QStringList moduleContributors;
  moduleContributors << QString("John Doe (AnyWare Corp.)");
  return moduleContributors;
}

//-----------------------------------------------------------------------------
QIcon qSlicerHyperionModuleCodeModule::icon() const
{
  return QIcon(":/Icons/HyperionModuleCode.png");
}

//-----------------------------------------------------------------------------
QStringList qSlicerHyperionModuleCodeModule::categories() const
{
  return QStringList() << "Examples";
}

//-----------------------------------------------------------------------------
QStringList qSlicerHyperionModuleCodeModule::dependencies() const
{
  return QStringList();
}

//-----------------------------------------------------------------------------
void qSlicerHyperionModuleCodeModule::setup()
{
  this->Superclass::setup();
}

//-----------------------------------------------------------------------------
qSlicerAbstractModuleRepresentation* qSlicerHyperionModuleCodeModule
::createWidgetRepresentation()
{
  return new qSlicerHyperionModuleCodeModuleWidget;
}

//-----------------------------------------------------------------------------
vtkMRMLAbstractLogic* qSlicerHyperionModuleCodeModule::createLogic()
{
  return vtkSlicerHyperionModuleCodeLogic::New();
}
